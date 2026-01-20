from datetime import datetime, date, timedelta, time
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.models import Doctor, Appointment, AvailabilitySlot
import httpx
from app.core.config import settings

async def get_doctor_by_name(session: AsyncSession, name: str) -> Optional[Doctor]:
    """Helper to find a doctor by fuzzy name matching."""
    # Try exact match first (case-insensitive)
    result = await session.execute(select(Doctor).where(Doctor.name.ilike(f"%{name}%")))
    doctor = result.scalars().first()
    
    if doctor:
        return doctor
    
    # If no match, try matching just the last name
    # e.g., "Dr. Smith" should match "Dr. Sarah Smith"
    name_parts = name.split()
    if len(name_parts) >= 2:
        last_name = name_parts[-1]
        result = await session.execute(select(Doctor).where(Doctor.name.ilike(f"%{last_name}%")))
        return result.scalars().first()
    
    return None

async def check_doctor_availability(
    doctor_name: str,
    date_str: str,  # YYYY-MM-DD
    time_preference: Optional[str] = None
) -> Dict[str, Any]:
    """
    Checks availability for a specific doctor on a given date.
    """
    async with AsyncSessionLocal() as session:
        doctor = await get_doctor_by_name(session, doctor_name)
        if not doctor:
            return {"error": f"Doctor '{doctor_name}' not found."}

        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD."}

        day_of_week = target_date.weekday() # 0=Monday

        # 1. Get availability slots config for this doctor on this day
        stmt = select(AvailabilitySlot).where(
            and_(
                AvailabilitySlot.doctor_id == doctor.id,
                AvailabilitySlot.day_of_week == day_of_week
            )
        )
        result = await session.execute(stmt)
        availability_configs = result.scalars().all()

        if not availability_configs:
            return {"doctor": doctor.name, "date": date_str, "available_slots": [], "message": "Doctor is not working on this day."}

        # 2. Get existing appointments
        start_of_day = datetime.combine(target_date, time.min)
        end_of_day = datetime.combine(target_date, time.max)
        
        appt_stmt = select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_time >= start_of_day,
                Appointment.appointment_time <= end_of_day,
                Appointment.status != "cancelled"
            )
        )
        appt_result = await session.execute(appt_stmt)
        booked_appointments = appt_result.scalars().all()
        
        booked_times = set()
        # Define local timezone (IST for this user/clinic)
        # In a real app, this should be configurable per doctor/clinic
        ist_offset = timedelta(hours=5, minutes=30)
        from datetime import timezone
        ist_tz = timezone(ist_offset)

        for appt in booked_appointments:
             # Convert DB time (likely UTC) to Clinic Time
             if appt.appointment_time.tzinfo:
                 local_dt = appt.appointment_time.astimezone(ist_tz)
                 booked_times.add(local_dt.time())
             else:
                 booked_times.add(appt.appointment_time.time())

        # 3. Generate slots
        available_slots = []
        for config in availability_configs:
            current_time = datetime.combine(target_date, config.start_time)
            end_time = datetime.combine(target_date, config.end_time)
            
            while current_time + timedelta(minutes=config.slot_duration_minutes) <= end_time:
                slot_time = current_time.time()
                
                # Check collision
                if slot_time not in booked_times:
                   available_slots.append(slot_time.strftime("%H:%M"))
                
                current_time += timedelta(minutes=config.slot_duration_minutes)


        return {
            "doctor_id": doctor.id,
            "doctor_name": doctor.name,
            "date": date_str,
            "available_slots": available_slots
        }

async def book_appointment(
    doctor_id: int,
    patient_name: str,
    patient_email: str,
    appointment_time_str: str, # ISO Format YYYY-MM-DDTHH:MM:SS
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Books an appointment.
    """
    async with AsyncSessionLocal() as session:
        try:
            appt_time = datetime.strptime(appointment_time_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
             # Try without seconds if it fails
             try:
                 appt_time = datetime.strptime(appointment_time_str, "%Y-%m-%dT%H:%M")
             except ValueError:
                 return {"status": "failed", "error": "Invalid time format. Use ISO format."}

        # Check if slot is still free (Double check)
        stmt = select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_time == appt_time,
                Appointment.status != "cancelled"
            )
        )
        result = await session.execute(stmt)
        if result.scalars().first():
            return {"status": "failed", "error": "Slot already taken."}

        new_appt = Appointment(
            doctor_id=doctor_id,
            patient_name=patient_name,
            patient_email=patient_email,
            appointment_time=appt_time,
            reason=reason,
            status="scheduled"
        )
        session.add(new_appt)
        await session.commit()
        await session.refresh(new_appt)
        
        # Fetch doctor details for notifications
        doctor = await session.get(Doctor, doctor_id)
        doctor_name = doctor.name if doctor else f"ID {doctor_id}"

        
        # --- Google Calendar Integration ---
        from app.services.google_calendar import calendar_service
        
        # Calculate end time (assuming 30 mins for now, or fetch slot duration)
        #Ideally get this from availability slot config, but default 30m is fine for MVP
        end_time = appt_time + timedelta(minutes=30)
        
        calendar_link = calendar_service.create_event(
            summary=f"Appointment with {doctor_name} - {patient_name}",
            start_time=appt_time,
            end_time=end_time,
            attendee_email=patient_email
        )
        
        # --- Email Integration ---
        from app.services.email_service import email_service
        # We don't await here to avoid blocking the user response, or we can await for better reliability
        # In FastAPI, we could use BackgroundTasks, but for simplicity here we await
        email_sent = await email_service.send_appointment_confirmation(
            patient_email=patient_email,
            patient_name=patient_name,
            appt_time=appt_time.strftime("%Y-%m-%d %H:%M"),
            doctor_name=doctor_name,
            calendar_link=calendar_link
        )

        msg = "Appointment booked successfully."
        if calendar_link:
            msg += f" Added to Google Calendar: {calendar_link}"
        else:
             msg += " (Calendar sync skipped: No credentials found)"
             
        if not email_sent:
            msg += " (Email delivery failed. Please check SMTP settings.)"
        elif not settings.SMTP_USER:
            msg += " (Email simulation active: No SMTP credentials found.)"
        else:
            msg += " Confirmation email sent successfully."

        # --- Slack Notification ---
        # Notify the doctor about the new appointment in a structured way
        notification_msg = (
            f"*New appointment scheduled!*\n"
            f"• *Patient:* {patient_name}\n"
            f"• *Time:* {appt_time.strftime('%Y-%m-%d %H:%M')}\n"
            f"• *Reason:* {reason or 'Not specified'}"
        )
        await send_doctor_notification(doctor_name, notification_msg)

        return {
            "status": "success",
            "appointment_id": new_appt.id,
            "message": msg,
            "calendar_link": calendar_link
        }

async def get_appointment_stats(
    doctor_name: str,
    query_type: str, # 'today', 'tomorrow', 'this_week'
    filter_by: Optional[str] = None
) -> Dict[str, Any]:
    """
    Gets appointment statistics for a doctor.
    """
    async with AsyncSessionLocal() as session:
        doctor = await get_doctor_by_name(session, doctor_name)
        if not doctor:
            return {"error": f"Doctor '{doctor_name}' not found."}

        today = date.today()
        start_date = None
        end_date = None

        if query_type in ["today", "daily"]:
            start_date = datetime.combine(today, time.min)
            end_date = datetime.combine(today, time.max)
        elif query_type == "tomorrow":
            tomorrow = today + timedelta(days=1)
            start_date = datetime.combine(tomorrow, time.min)
            end_date = datetime.combine(tomorrow, time.max)
        elif query_type == "yesterday":
             yesterday = today - timedelta(days=1)
             start_date = datetime.combine(yesterday, time.min)
             end_date = datetime.combine(yesterday, time.max)
        elif query_type in ["this_week", "weekly"]:
             # Assuming week starts Monday
             start_date = datetime.combine(today - timedelta(days=today.weekday()), time.min)
             end_date = datetime.combine(start_date + timedelta(days=6), time.max)
        else:
             return {"error": "Invalid query_type"}

        # Build Query
        stmt = select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_time >= start_date,
                Appointment.appointment_time <= end_date
            )
        )

        if filter_by:
            stmt = stmt.where(Appointment.reason.ilike(f"%{filter_by}%"))

        result = await session.execute(stmt)
        appointments = result.scalars().all()

        return {
            "doctor_name": doctor.name,
            "period": query_type,
            "total_appointments": len(appointments),
            "appointments": [
                {
                    "time": appt.appointment_time.strftime("%H:%M"),
                    "patient": appt.patient_name,
                    "reason": appt.reason
                }
                for appt in appointments
            ]
        }


async def send_doctor_notification(
    doctor_name: str,
    message: str,
    channel: str = "slack"
) -> Dict[str, Any]:
    """
    Sends a notification to the doctor via Slack Webhook.
    """
    webhook_url = settings.SLACK_WEBHOOK_URL
    
    if not webhook_url:
        print(f"Mock Notification to {doctor_name}: {message}")
        return {
            "status": "success",
            "mode": "mock",
            "recipient": doctor_name,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

    # Premium Slack Payload Design
    # We use 'attachments' to get the colored sidebar (blue for info) which feels more 'premium'
    # than just plain blocks.
    
    # Simple logic to split message into an intro and body if possible
    lines = message.strip().split('\n')
    intro = lines[0] if lines else "New Update"
    body = "\n".join(lines[1:]) if len(lines) > 1 else ""

    payload = {
        "attachments": [
            {
                "color": "#36a64f", # Health green
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🏥 MediAssist Professional",
                            "emoji": True
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Hello {doctor_name},*\n{intro}"
                        }
                    }
                ]
            }
        ]
    }

    if body:
        payload["attachments"][0]["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": body
            }
        })

    # Add footer context
    payload["attachments"][0]["blocks"].extend([
        {
            "type": "divider"
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📅 *Issued:* {datetime.now().strftime('%b %d, %Y | %H:%M')}  •  🤖 *AI Assistant*"
                }
            ]
        }
    ])

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(webhook_url, json=payload)
            resp.raise_for_status()
            
        return {
            "status": "success",
            "mode": "live",
            "channel": "slack",
            "recipient": doctor_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Failed to send Slack notification: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "recipient": doctor_name
        }

async def list_doctors(specialization: Optional[str] = None) -> Dict[str, Any]:
    """
    Lists all available doctors, optionally filtering by specialization.
    """
    async with AsyncSessionLocal() as session:
        # Map common terms to medical specializations
        specialization_map = {
            "heart": "Cardiologist",
            "heart doctor": "Cardiologist",
            "cardiac": "Cardiologist",
            "tooth": "Dentist",
            "dental": "Dentist",
            "teeth": "Dentist",
            "bone": "Orthopedic",
            "skin": "Dermatologist",
            "eye": "Ophthalmologist",
            "brain": "Neurologist",
            "child": "Pediatrician",
            "kids": "Pediatrician",
            "baby": "Pediatrician",
        }
        
        # Convert common terms to medical specialization
        if specialization:
            spec_lower = specialization.lower()
            for key, value in specialization_map.items():
                if key in spec_lower:
                    specialization = value
                    break
        
        stmt = select(Doctor)
        if specialization:
            stmt = stmt.where(Doctor.specialization.ilike(f"%{specialization}%"))
        
        result = await session.execute(stmt)
        doctors = result.scalars().all()
        return {
            "doctors": [
                {"id": d.id, "name": d.name, "specialization": d.specialization} 
                for d in doctors
            ]
        }

