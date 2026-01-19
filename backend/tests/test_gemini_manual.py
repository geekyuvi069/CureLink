import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from dotenv import load_dotenv
# Load .env file explicitly
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), ".env")
load_dotenv(env_path, override=True) # Force reload

# Ensure we use the proper env (though llm_service loads from settings, settings loads from .env)
# The .env file should be present now.

from app.services.llm_service import process_chat_message

async def test_gemini_flow():
    print("--- Testing Gemini Agent Flow ---")
    
    # 1. Simple Hello
    print("\n1. User: Hello")
    res1 = await process_chat_message("Hello!")
    print(f"Agent: {res1['response']}")
    session_id = res1['session_id']
    # session_id = None # Create new session for tool test
    
    # 2. Ask for availability (Tool Call)
    print("\n2. User: Check Dr. Ahuja's availability for next Monday")
    res2 = await process_chat_message("Check Dr. Ahuja's availability for next Monday", session_id=session_id)
    print(f"Agent: {res2['response']}")

    # 3. Book (Sequential Tool Call)
    print("\n3. User: Book the first available slot for John Doe (john@example.com) for fever")
    res3 = await process_chat_message("Book the first available slot for John Doe (john@example.com) for fever", session_id=session_id)
    print(f"Agent: {res3['response']}")

if __name__ == "__main__":
    asyncio.run(test_gemini_flow())
