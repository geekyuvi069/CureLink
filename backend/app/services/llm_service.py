import json
import uuid
import os
from typing import List, Dict, Any, Optional
from sqlalchemy.future import select
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from google.api_core.exceptions import InvalidArgument

from app.core.database import AsyncSessionLocal
from app.models.models import ConversationSession
from app.core.config import settings
from app.core.tools import AVAILABLE_TOOLS  # We will use the functions directly
from datetime import datetime

# Configure Gemini
if settings.GEMINI_API_KEY:
    os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
    genai.configure(api_key=settings.GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY is not set.")

# Get current date for context
current_date = datetime.now().strftime("%Y-%m-%d")
current_day = datetime.now().strftime("%A")

# Initialize Model with Tools
tools_list = list(AVAILABLE_TOOLS.values())

model = genai.GenerativeModel(
    model_name='gemini-flash-latest',
    tools=tools_list,
    system_instruction=f"""
You are a smart and helpful Doctor Appointment Assistant.
Your goal is to help patients book appointments and help doctors get reports.

CURRENT DATE CONTEXT:
- Today's date is: {current_date}
- Today is: {current_day}
- Use this information to calculate "tomorrow", "next week", etc.

DATE HANDLING:
1. When users say "tomorrow", "today", "next week", etc., YOU MUST convert it to YYYY-MM-DD format.
2. Calculate the actual date based on the current date and pass it to tools.
3. Example: If today is 2026-01-20 and user says "tomorrow", use "2026-01-21".

DOCTOR MATCHING:
1. Be flexible with doctor names - "Dr. Smith" could match "Dr. Sarah Smith".
2. If exact match fails, try partial matching.
3. Common name variations: "Dr. Ahuja" = "Dr. Rajesh Ahuja", "Dr. Smith" = "Dr. Sarah Smith".

SPECIALIZATION MATCHING:
1. Understand common terms: "heart doctor" = "Cardiologist", "tooth doctor" = "Dentist".
2. Map user-friendly terms to medical specializations.
3. If unsure, list doctors and let user choose.

SLACK NOTIFICATION FORMATTING:
1. When using `send_doctor_notification`, structured messages look best.
2. The FIRST line should be a clear introduction (e.g., "I've found your appointments for tomorrow.")
3. Subsequent lines should contain the specific details using bullet points (•).
4. Example:
   I have found 2 appointments for you today:
   • 10:00: Patient X (Reason)
   • 11:30: Patient Y (Reason)

REPORTING RULES:
1. When a doctor asks for a report (daily, weekly, today, tomorrow, etc.), ALWAYS use the `get_appointment_stats` tool.
2. The `query_type` parameter supports: "today", "tomorrow", "yesterday", "this_week", "daily", "weekly".
3. If a user says "weekly", use `query_type="weekly"`. If "daily", use `query_type="daily"`.
4. If a tool returns an empty list, inform the doctor politely that no appointments were found for that period.

BOOKING RULES:
1. ALWAYS check availability before booking using `check_doctor_availability`.
2. If details (Name, Email, Reason) are missing, ASK for them.
3. The `book_appointment` tool is the ONLY way to send emails.
4. If you don't know a doctor's ID, use `list_doctors` first. NEVER guess an ID.
5. If a doctor asks for specific patients (e.g. "patients with fever"), use the `filter_by` parameter.
"""
)

async def get_or_create_session(session_id: Optional[str] = None, user_id: Optional[int] = None) -> ConversationSession:
    async with AsyncSessionLocal() as db:
        if session_id:
            result = await db.execute(select(ConversationSession).where(ConversationSession.session_id == session_id))
            session = result.scalars().first()
            if session:
                return session
        
        # Create new session
        new_id = str(uuid.uuid4())
        session = ConversationSession(
            session_id=new_id,
            user_id=user_id,
            messages=[],
            context={}
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

async def update_session_messages(session_id: str, new_messages: List[Dict]):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(ConversationSession).where(ConversationSession.session_id == session_id))
        session = result.scalars().first()
        if session:
            current_msgs = list(session.messages)
            current_msgs.extend(new_messages)
            if len(current_msgs) > 60: 
                current_msgs = current_msgs[-60:]
            session.messages = current_msgs
            await db.commit()

async def process_chat_message(user_message: str, session_id: Optional[str] = None, user_id: Optional[int] = None) -> Dict[str, Any]:
    session = await get_or_create_session(session_id, user_id)
    
    # helper to map roles
    def map_role(r):
        if r == 'assistant':
            return 'model'
        # Gemini history often requires 'user' role for function response turns
        return 'user'

    # Reconstruct History
    # We include function calls and responses to maintain context
    from google.generativeai import protos
    gemini_history = []
    
    for msg in session.messages:
        role = map_role(msg['role'])
        content = msg.get('content')
        tool_call = msg.get('tool_call')
        tool_response = msg.get('tool_response')
        
        parts = []
        if content:
            parts.append(protos.Part(text=content))
        
        if tool_call:
             parts.append(protos.Part(
                 function_call=protos.FunctionCall(
                     name=tool_call['name'],
                     args=tool_call['args']
                 )
             ))
        
        if tool_response:
             parts.append(protos.Part(
                 function_response=protos.FunctionResponse(
                     name=tool_response['name'],
                     response={"result": tool_response['result']}
                 )
             ))
             
        if parts:
            # If the last message was also the same role, we might want to merge parts?
            # But in function calling, they should be distinct turns.
            # However, tool_response MUST have a non-model role.
            if tool_response:
                role = 'user' # Force user role for function responses
            
            gemini_history.append({"role": role, "parts": parts})
    
    # --- SANITIZATION: Fix Broken Tool Chains due to Truncation ---
    # Ensure history doesn't start with a function_response (orphaned)
    while gemini_history and gemini_history[0]["parts"][0].function_response:
        print("Sanitizing history: Removing orphaned function_response at start.")
        gemini_history.pop(0)

    # Ensure history doesn't start with a model function_call that has no user response following it immediately?
    # Actually, Gemini might tolerate a call at start, but let's be safe. 
    # The more critical one is function_response without call.
    # Also remove if first message is 'model' but not a function call? 
    # (Gemini usually okay with Model starting, but typically User starts).
    
    # Basic check: If sanitized history is empty, that's fine (new chat).
    
    chat = model.start_chat(history=gemini_history)
    
    try:
        # 1. Store User Message in DB first to ensure correct Turn order in history
        await update_session_messages(session.session_id, [{"role": "user", "content": user_message}])

        # 2. Send User Message to Gemini
        print(f"Sending to Gemini: {user_message}")
        response = await chat.send_message_async(user_message)
        print("Received response from Gemini.")
        
        # 2. Loop for Tool Calls
        final_text = ""
        
        while True:
            if not response.parts:
                try:
                    final_text = response.text
                except Exception as e:
                     print(f"Error accessing response.text: {e}")
                     final_text = ""
                break

            # Check if ANY part is a function call
            function_call_part = None
            for p in response.parts:
                if p.function_call:
                    function_call_part = p
                    break
            
            if function_call_part:
                fc = function_call_part.function_call
                tool_name = fc.name
                tool_args = dict(fc.args)
                
                print(f"Executing Tool: {tool_name} with args: {tool_args}")
                
                if tool_name in AVAILABLE_TOOLS:
                    tool_func = AVAILABLE_TOOLS[tool_name]
                    try:
                        tool_result = await tool_func(**tool_args)
                    except Exception as e:
                        tool_result = {"error": str(e)}
                else:
                    tool_result = {"error": f"Tool {tool_name} not found"}
                
                print(f"Tool Result: {tool_result}")

                # Store tool call and response in history
                await update_session_messages(session.session_id, [
                    {
                        "role": "assistant", 
                        "content": None, 
                        "tool_call": {"name": tool_name, "args": tool_args}
                    },
                    {
                        "role": "user", # Function responses are stored as 'user' to maintain turn consistency
                        "content": None, 
                        "tool_response": {"name": tool_name, "result": tool_result}
                    }
                ])

                # Send result back to model
                from google.generativeai import protos
                
                response = await chat.send_message_async(
                    [
                        protos.Part(
                            function_response=protos.FunctionResponse(
                                name=tool_name,
                                response={"result": tool_result}
                            )
                        )
                    ]
                )
                # Loop continues
            
            else:
                # Manual text construction with strict safety checks
                text_parts = []
                for p in response.parts:
                    # Skip function calls explicitly before touching .text
                    if p.function_call:
                        continue
                    
                    try:
                        if p.text:
                            text_parts.append(p.text)
                    except Exception as e:
                        print(f"Skipping part due to text access error: {e}")
                        continue
                
                final_text = "".join(text_parts)
                
                # If still empty, try response.text as last resort fallback
                if not final_text:
                    try:
                        final_text = response.text
                    except Exception:
                        pass
                
                break

    except Exception as e:
        final_text = f"Error communicating with AI: {str(e)}"
        print(f"Gemini Error Details: {e}")

    # Update DB with Final Assistant Response
    await update_session_messages(session.session_id, [{"role": "assistant", "content": final_text}])
    
    return {
        "response": final_text,
        "session_id": session.session_id
    }
