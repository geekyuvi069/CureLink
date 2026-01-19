import asyncio
from app.core.database import AsyncSessionLocal
from app.models.models import User, Doctor, AvailabilitySlot
from app.core.security import get_password_hash
from datetime import time

async def seed_data():
    print("Seeding Initial Data...")
    async with AsyncSessionLocal() as db:
        # Create a Demo Doctor User
        hashed_pw = get_password_hash("doctor123")
        doctor_user = User(
            email="doctor@test.com",
            hashed_password=hashed_pw,
            role="doctor",
            full_name="Dr. Ahuja"
        )
        db.add(doctor_user)
        await db.commit()
        await db.refresh(doctor_user)

        # Create Doctor Profile
        doctor_profile = Doctor(
            name="Dr. Ahuja",
            email="doctor@test.com",
            specialization="General Physician",
            user_id=doctor_user.id
        )
        db.add(doctor_profile)
        await db.commit()
        await db.refresh(doctor_profile)

        # Add some availability slots
        slots = [
            AvailabilitySlot(doctor_id=doctor_profile.id, day_of_week=0, start_time=time(9, 0), end_time=time(12, 0)),
            AvailabilitySlot(doctor_id=doctor_profile.id, day_of_week=1, start_time=time(14, 0), end_time=time(17, 0)),
            AvailabilitySlot(doctor_id=doctor_profile.id, day_of_week=2, start_time=time(10, 0), end_time=time(13, 0)),
        ]
        db.add_all(slots)
        await db.commit()

        # Create a Demo Patient User
        patient_pw = get_password_hash("patient123")
        patient_user = User(
            email="patient@test.com",
            hashed_password=patient_pw,
            role="patient",
            full_name="John Doe"
        )
        db.add(patient_user)
        await db.commit()

    print("Seeding complete! You can login with:")
    print("Doctor: doctor@test.com / doctor123")
    print("Patient: patient@test.com / patient123")

if __name__ == "__main__":
    asyncio.run(seed_data())
