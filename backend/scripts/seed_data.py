import asyncio
import sys
import os
from datetime import time, datetime
from sqlalchemy import select

# Add the project root to the python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models.models import Doctor, AvailabilitySlot

doctors_data = [
    {
        "name": "Dr. Rajesh Ahuja", "email": "ahuja@hospital.com", "specialization": "General Physician",
        "phone": "+91-9876543210", "experience_years": 15, "qualification": "MBBS, MD",
        "consultation_fee": 500, "available_days": ["Monday", "Wednesday", "Friday"], "available_hours": "9:00 AM - 5:00 PM"
    },
    {
        "name": "Dr. Sarah Smith", "email": "smith@hospital.com", "specialization": "Cardiologist",
        "phone": "+91-9876543211", "experience_years": 20, "qualification": "MBBS, MD, DM (Cardiology)",
        "consultation_fee": 1200, "available_days": ["Tuesday", "Thursday", "Saturday"], "available_hours": "10:00 AM - 4:00 PM"
    },
    {
        "name": "Dr. Michael Molar", "email": "molar@hospital.com", "specialization": "Dentist",
        "phone": "+91-9876543212", "experience_years": 12, "qualification": "BDS, MDS",
        "consultation_fee": 800, "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "available_hours": "9:00 AM - 6:00 PM"
    },
    {
        "name": "Dr. Priya Sharma", "email": "sharma@hospital.com", "specialization": "Pediatrician",
        "phone": "+91-9876543213", "experience_years": 10, "qualification": "MBBS, MD (Pediatrics)",
        "consultation_fee": 700, "available_days": ["Monday", "Wednesday", "Friday", "Saturday"], "available_hours": "8:00 AM - 2:00 PM"
    },
    {
        "name": "Dr. James Wilson", "email": "wilson@hospital.com", "specialization": "Orthopedic Surgeon",
        "phone": "+91-9876543214", "experience_years": 18, "qualification": "MBBS, MS (Orthopedics)",
        "consultation_fee": 1000, "available_days": ["Tuesday", "Thursday", "Saturday"], "available_hours": "11:00 AM - 5:00 PM"
    },
    {
        "name": "Dr. Anita Desai", "email": "desai@hospital.com", "specialization": "Gynecologist",
        "phone": "+91-9876543215", "experience_years": 16, "qualification": "MBBS, MD (OB-GYN)",
        "consultation_fee": 900, "available_days": ["Monday", "Tuesday", "Thursday", "Friday"], "available_hours": "9:00 AM - 3:00 PM"
    },
    {
        "name": "Dr. Robert Chen", "email": "chen@hospital.com", "specialization": "Neurologist",
        "phone": "+91-9876543216", "experience_years": 22, "qualification": "MBBS, MD, DM (Neurology)",
        "consultation_fee": 1500, "available_days": ["Wednesday", "Friday", "Saturday"], "available_hours": "10:00 AM - 4:00 PM"
    },
    {
        "name": "Dr. Kavita Reddy", "email": "reddy@hospital.com", "specialization": "Dermatologist",
        "phone": "+91-9876543217", "experience_years": 8, "qualification": "MBBS, MD (Dermatology)",
        "consultation_fee": 800, "available_days": ["Monday", "Wednesday", "Friday"], "available_hours": "2:00 PM - 7:00 PM"
    },
    {
        "name": "Dr. David Kumar", "email": "kumar@hospital.com", "specialization": "Ophthalmologist",
        "phone": "+91-9876543218", "experience_years": 14, "qualification": "MBBS, MS (Ophthalmology)",
        "consultation_fee": 750, "available_days": ["Tuesday", "Thursday", "Saturday"], "available_hours": "9:00 AM - 5:00 PM"
    },
    {
        "name": "Dr. Meera Patel", "email": "patel@hospital.com", "specialization": "Psychiatrist",
        "phone": "+91-9876543219", "experience_years": 11, "qualification": "MBBS, MD (Psychiatry)",
        "consultation_fee": 1100, "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday"], "available_hours": "3:00 PM - 8:00 PM"
    },
    {
        "name": "Dr. Thomas Anderson", "email": "anderson@hospital.com", "specialization": "ENT Specialist",
        "phone": "+91-9876543220", "experience_years": 13, "qualification": "MBBS, MS (ENT)",
        "consultation_fee": 850, "available_days": ["Monday", "Wednesday", "Friday", "Saturday"], "available_hours": "10:00 AM - 4:00 PM"
    },
    {
        "name": "Dr. Lakshmi Iyer", "email": "iyer@hospital.com", "specialization": "Endocrinologist",
        "phone": "+91-9876543221", "experience_years": 9, "qualification": "MBBS, MD, DM (Endocrinology)",
        "consultation_fee": 1000, "available_days": ["Tuesday", "Thursday", "Saturday"], "available_hours": "9:00 AM - 3:00 PM"
    },
    {
        "name": "Dr. William Brown", "email": "brown@hospital.com", "specialization": "Gastroenterologist",
        "phone": "+91-9876543222", "experience_years": 17, "qualification": "MBBS, MD, DM (Gastroenterology)",
        "consultation_fee": 1300, "available_days": ["Monday", "Wednesday", "Friday"], "available_hours": "11:00 AM - 5:00 PM"
    },
    {
        "name": "Dr. Sunita Joshi", "email": "joshi@hospital.com", "specialization": "Radiologist",
        "phone": "+91-9876543223", "experience_years": 12, "qualification": "MBBS, MD (Radiology)",
        "consultation_fee": 900, "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "available_hours": "8:00 AM - 4:00 PM"
    },
    {
        "name": "Dr. Christopher Lee", "email": "lee@hospital.com", "specialization": "Urologist",
        "phone": "+91-9876543224", "experience_years": 15, "qualification": "MBBS, MS (Urology)",
        "consultation_fee": 1100, "available_days": ["Tuesday", "Thursday", "Saturday"], "available_hours": "10:00 AM - 4:00 PM"
    },
    {
        "name": "Dr. Neha Gupta", "email": "gupta@hospital.com", "specialization": "Pulmonologist",
        "phone": "+91-9876543225", "experience_years": 10, "qualification": "MBBS, MD, DM (Pulmonology)",
        "consultation_fee": 950, "available_days": ["Monday", "Wednesday", "Friday", "Saturday"], "available_hours": "9:00 AM - 3:00 PM"
    },
    {
        "name": "Dr. Richard Martinez", "email": "martinez@hospital.com", "specialization": "Nephrologist",
        "phone": "+91-9876543226", "experience_years": 19, "qualification": "MBBS, MD, DM (Nephrology)",
        "consultation_fee": 1250, "available_days": ["Tuesday", "Thursday", "Saturday"], "available_hours": "11:00 AM - 5:00 PM"
    },
    {
        "name": "Dr. Pooja Nair", "email": "nair@hospital.com", "specialization": "Oncologist",
        "phone": "+91-9876543227",
        "experience_years": 14,
        "qualification": "MBBS, MD, DM (Oncology)",
        "consultation_fee": 1800,
        "available_days": ["Monday", "Wednesday", "Friday"], "available_hours": "10:00 AM - 4:00 PM"
    },
    {
        "name": "Dr. Daniel Thompson", "email": "thompson@hospital.com", "specialization": "Anesthesiologist",
        "phone": "+91-9876543228", "experience_years": 16, "qualification": "MBBS, MD (Anesthesiology)",
        "consultation_fee": 800, "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "available_hours": "7:00 AM - 3:00 PM"
    },
    {
        "name": "Dr. Sneha Menon", "email": "menon@hospital.com", "specialization": "Rheumatologist",
        "phone": "+91-9876543229",
        "experience_years": 11,
        "qualification": "MBBS, MD, DM (Rheumatology)",
        "consultation_fee": 1050,
        "available_days": ["Tuesday", "Thursday", "Saturday"], "available_hours": "9:00 AM - 3:00 PM"
    }
]

DAYS_MAP = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
}

def parse_time_range(range_str):
    # expect "9:00 AM - 5:00 PM"
    start_str, end_str = range_str.split(" - ")
    start_dt = datetime.strptime(start_str, "%I:%M %p").time()
    end_dt = datetime.strptime(end_str, "%I:%M %p").time()
    return start_dt, end_dt

async def seed_data():
    async with AsyncSessionLocal() as session:
        print("Starting seed process for 20 specialists...")
        
        for doc_data in doctors_data:
            stmt = select(Doctor).where(Doctor.email == doc_data["email"])
            result = await session.execute(stmt)
            existing_doc = result.scalars().first()

            if not existing_doc:
                # Mock slack_id if not present
                slack_id = f"U{doc_data['phone'][-8:]}" 
                
                new_doc = Doctor(
                    name=doc_data["name"],
                    email=doc_data["email"],
                    specialization=doc_data["specialization"],
                    slack_id=slack_id,
                    phone=doc_data["phone"],
                    experience_years=doc_data["experience_years"],
                    qualification=doc_data["qualification"],
                    consultation_fee=doc_data["consultation_fee"]
                )
                session.add(new_doc)
                await session.commit()
                await session.refresh(new_doc)
                print(f"Created doctor: {new_doc.name}")

                # Create slots
                start_t, end_t = parse_time_range(doc_data["available_hours"])
                slots = []
                for day_name in doc_data["available_days"]:
                    day_idx = DAYS_MAP.get(day_name)
                    if day_idx is not None:
                        # Add a big block, or split? Let's add a big block for simplicity
                        slots.append(AvailabilitySlot(
                            doctor_id=new_doc.id,
                            day_of_week=day_idx,
                            start_time=start_t,
                            end_time=end_t
                        ))
                
                if slots:
                    session.add_all(slots)
                    await session.commit()
                    print(f"  Added {len(slots)} schedule blocks for {new_doc.name}")

            else:
                # Update existing doctor with new fields if they are missing/default
                if existing_doc.experience_years == 0:
                     existing_doc.experience_years = doc_data["experience_years"]
                     existing_doc.qualification = doc_data["qualification"]
                     existing_doc.consultation_fee = doc_data["consultation_fee"]
                     # We might want to update name too if it changed from "Dr. Ahuja" to "Dr. Rajesh Ahuja"
                     existing_doc.name = doc_data["name"]
                     session.add(existing_doc)
                     await session.commit()
                     print(f"Updated info for {existing_doc.name}")
                else:
                    print(f"Doctor {existing_doc.name} already exists.")

if __name__ == "__main__":
    asyncio.run(seed_data())
