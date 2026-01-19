import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models.models import Appointment, Doctor

async def seed_appointments():
    async with AsyncSessionLocal() as session:
        # Get Dr. Ahuja
        from sqlalchemy import select
        result = await session.execute(select(Doctor).where(Doctor.name == "Dr. Ahuja"))
        dr_ahuja = result.scalars().first()
        
        if not dr_ahuja:
            print("Dr. Ahuja not found. Run seed_data.py first.")
            return

        today = datetime.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        test_appts = [
            # Yesterday
            Appointment(
                doctor_id=dr_ahuja.id,
                patient_name="John Doe",
                patient_email="john@example.com",
                appointment_time=yesterday.replace(hour=10, minute=0, second=0, microsecond=0),
                reason="Fever and cold",
                status="completed"
            ),
            Appointment(
                doctor_id=dr_ahuja.id,
                patient_name="Jane Smith",
                patient_email="jane@example.com",
                appointment_time=yesterday.replace(hour=14, minute=30, second=0, microsecond=0),
                reason="Routine checkup",
                status="completed"
            ),
            # Today
            Appointment(
                doctor_id=dr_ahuja.id,
                patient_name="Alice Brown",
                patient_email="alice@example.com",
                appointment_time=today.replace(hour=11, minute=0, second=0, microsecond=0),
                reason="Severe Headache",
                status="scheduled"
            ),
            Appointment(
                doctor_id=dr_ahuja.id,
                patient_name="Bob Wilson",
                patient_email="bob@example.com",
                appointment_time=today.replace(hour=15, minute=0, second=0, microsecond=0),
                reason="Fever",
                status="scheduled"
            ),
            # Tomorrow
            Appointment(
                doctor_id=dr_ahuja.id,
                patient_name="Charlie Davis",
                patient_email="charlie@example.com",
                appointment_time=tomorrow.replace(hour=9, minute=30, second=0, microsecond=0),
                reason="Back Pain",
                status="scheduled"
            )
        ]

        session.add_all(test_appts)
        await session.commit()
        print(f"Added {len(test_appts)} test appointments for Dr. Ahuja.")

if __name__ == "__main__":
    asyncio.run(seed_appointments())
