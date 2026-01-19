import asyncio
from app.core.database import engine, Base
from app.models.models import User, Doctor, Appointment, AvailabilitySlot, ConversationSession

async def init_db():
    print("Initializing Database...")
    try:
        async with engine.begin() as conn:
            # For a real DB, you might want to drop first if you want a clean slate
            # await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    asyncio.run(init_db())
