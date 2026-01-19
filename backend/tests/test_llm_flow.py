import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# Set dummy key for testing BEFORE importing service
os.environ["OPENAI_API_KEY"] = "sk-test-dummy-key"

from app.services.llm_service import process_chat_message

# Mocking OpenAI to test logic without keys
async def mock_openai_response(*args, **kwargs):
    # This is a very basic mock to test the structure
    messages = kwargs.get("messages", [])
    last_msg = messages[-1]["content"]
    
    mock_msg = MagicMock()
    
    if "book" in last_msg.lower():
         # Simulate a tool call response
         mock_msg.tool_calls = [
             MagicMock(
                 id="call_123",
                 function=MagicMock(
                     name="check_doctor_availability",
                     arguments='{"doctor_name": "Ahuja", "date": "2026-01-20"}'
                 )
             )
         ]
         mock_msg.content = None
    else:
        # Normal response
        mock_msg.tool_calls = None
        mock_msg.content = "I can help you with that."

    mock_choice = MagicMock()
    mock_choice.message = mock_msg
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    return mock_response

async def test_llm_flow():
    print("--- Testing LLM Agent Flow (Mocked) ---")
    
    # We patch the client.chat.completions.create method
    with patch("app.services.llm_service.client.chat.completions.create", side_effect=mock_openai_response) as mock_create:
        
        print("\n1. Testing 'Hello' (Simple text)...")
        res1 = await process_chat_message("Hello")
        print(f"Response: {res1['response']}")
        print(f"Session ID: {res1['session_id']}")

        print("\n2. Testing 'Book with Dr. Ahuja' (Should trigger tool)...")
        # Note: In our mock above, we only simulate the first turn of the tool call.
        # The loop in process_chat_message will call the tool, append result, and call LLM again.
        # We need our mock to handle the SECOND call (after tool output) to give a final answer.
        
        # Let's make the mock smarter via side_effect list or function
        # Simplified: valid tool call -> then final answer
        
        async def smart_mock(*args, **kwargs):
            messages = kwargs.get("messages", [])
            last_role = messages[-1]["role"]
            
            mock_msg = MagicMock()
            
            if last_role == "tool":
                 # Agent sees tool output, gives final answer
                 mock_msg.tool_calls = None
                 mock_msg.content = "Dr. Ahuja is available. Shall I book?"
            elif "book" in messages[-1]["content"].lower():
                 # Trigger tool
                 mock_msg.tool_calls = [
                     MagicMock(
                         id="call_123",
                         function=MagicMock(
                             name="check_doctor_availability",
                             arguments='{"doctor_name": "Ahuja", "date": "2026-01-20"}'
                         )
                     )
                 ]
                 mock_msg.content = None
            else:
                 mock_msg.tool_calls = None
                 mock_msg.content = "Hello there!"
            
            mock_choice = MagicMock()
            mock_choice.message = mock_msg
            mock_resp = MagicMock()
            mock_resp.choices = [mock_choice]
            return mock_resp

        mock_create.side_effect = smart_mock
        
        # Re-run test 2
        res2 = await process_chat_message("I want to book with Dr. Ahuja")
        print(f"Response: {res2['response']}")
        
        # Verify tool execution
        # We can't easily verify the print output of the tool execution here without capturing stdout,
        # but the fact that we got a final response after the tool mock means the loop worked.

if __name__ == "__main__":
    asyncio.run(test_llm_flow())
