import asyncio
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from app.services.llm_service import process_chat_message

async def test_context_flow():
    print("--- Testing Multi-Turn Context & Tool Aliases ---")
    
    # 1. Ask for doctor list
    print("\n[Turn 1] User: Show me the list of doctors")
    resp1 = await process_chat_message("Show me the list of doctors")
    print(f"AI: {resp1['response']}")
    session_id = resp1['session_id']
    
    # 2. Ask for stats using an alias and NO name (context check)
    print(f"\n[Turn 2] User: Give me the weekly report for him (Referencing Dr. Smith or Ahuja)")
    # Since Dr. Ahuja is usually first, let's see if it picks one or asks. 
    # But wait, Dr. Smith was the one user had trouble with.
    # Let's be more specific to force Dr. Smith context.
    
    print("\n[Turn 2] User: What about Dr. Smith?")
    resp2 = await process_chat_message("What about Dr. Smith?", session_id)
    print(f"AI: {resp2['response']}")
    
    print("\n[Turn 3] User: Give me his weekly report")
    resp3 = await process_chat_message("Give me his weekly report", session_id)
    print(f"AI: {resp3['response']}")
    
    if "Dr. Smith" in resp3['response'] or "Cardiologist" in resp3['response']:
        print("\n✅ Context SUCCESS: AI remembered Dr. Smith and fetched stats.")
    else:
        print("\n❌ Context FAILED: AI forgot the doctor's name.")

if __name__ == "__main__":
    asyncio.run(test_context_flow())
