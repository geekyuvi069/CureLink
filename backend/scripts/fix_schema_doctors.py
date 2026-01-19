import asyncio
import sys
import os
from sqlalchemy import text

# Add the project root to the python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from app.core.database import AsyncSessionLocal

async def add_doctor_columns():
    async with AsyncSessionLocal() as session:
        print("Adding new columns to doctors table...")
        try:
            await session.execute(text("ALTER TABLE doctors ADD COLUMN IF NOT EXISTS experience_years INTEGER DEFAULT 0;"))
            await session.execute(text("ALTER TABLE doctors ADD COLUMN IF NOT EXISTS qualification VARCHAR(255);"))
            await session.execute(text("ALTER TABLE doctors ADD COLUMN IF NOT EXISTS consultation_fee INTEGER DEFAULT 0;"))
            await session.commit()
            print("Columns added successfully.")
        except Exception as e:
            print(f"Error updating schema: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(add_doctor_columns())
