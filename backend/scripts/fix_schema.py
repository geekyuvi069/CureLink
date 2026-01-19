
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def update_schema():
    print("Updating database schema...")
    async with engine.begin() as conn:
        # Add messages column if it doesn't exist
        await conn.execute(text("ALTER TABLE conversation_sessions ADD COLUMN IF NOT EXISTS messages JSON DEFAULT '[]'"))
        # Add context column if it doesn't exist
        await conn.execute(text("ALTER TABLE conversation_sessions ADD COLUMN IF NOT EXISTS context JSON DEFAULT '{}'"))
        # Verify columns
        result = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='conversation_sessions'"))
        columns = [r[0] for r in result]
        print(f"Current columns in conversation_sessions: {columns}")

if __name__ == "__main__":
    asyncio.run(update_schema())
