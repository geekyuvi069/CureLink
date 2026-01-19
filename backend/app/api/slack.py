from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
import hmac
import hashlib
import time
import json
import httpx
from app.core.config import settings
from app.services.llm_service import process_chat_message

router = APIRouter()

async def verify_slack_signature(request: Request):
    """Verifies that the request actually came from Slack."""
    if not settings.SLACK_SIGNING_SECRET:
        return True # Skip verification if not configured
        
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    signature = request.headers.get("X-Slack-Signature")
    
    if not timestamp or not signature:
        raise HTTPException(status_code=400, detail="Missing Slack headers")
        
    if abs(time.time() - int(timestamp)) > 60 * 5:
        raise HTTPException(status_code=400, detail="Request too old")
        
    body = await request.body()
    sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
    my_signature = "v0=" + hmac.new(
        settings.SLACK_SIGNING_SECRET.encode("utf-8"),
        sig_basestring.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(my_signature, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

async def send_slack_message(channel: str, text: str):
    """Helper to send a message back to Slack."""
    if not settings.SLACK_BOT_TOKEN:
        print(f"No SLACK_BOT_TOKEN. Mock reply: {text}")
        return
        
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}"}
    payload = {"channel": channel, "text": text}
    
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload, headers=headers)

async def handle_slack_message(event: dict):
    """Processes the message via LLM and replies to Slack."""
    user_id = event.get("user")
    channel_id = event.get("channel")
    text = event.get("text")
    
    if event.get("bot_id"): # Ignore bot's own messages
        return

    import re
    text = re.sub(r'<@U[A-Z0-9]+>', '', text).strip()

    # Create a unique session ID for this Slack user
    session_id = f"slack_{user_id}"
    
    # Process with Gemini
    response_data = await process_chat_message(text, session_id)
    ai_response = response_data.get("response", "I'm sorry, I couldn't process that.")
    
    # Reply back
    await send_slack_message(channel_id, ai_response)

@router.post("/events")
async def slack_events(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    
    # 1. Handle URL Verification (Slack Challenge)
    if data.get("type") == "url_verification":
        return {"challenge": data.get("challenge")}
        
    # 2. Verify Signature for real events
    await verify_slack_signature(request)
    
    # 3. Handle Events (messages & mentions)
    event = data.get("event")
    if event and event.get("type") in ["message", "app_mention"] and not event.get("subtype"):
        background_tasks.add_task(handle_slack_message, event)
        
    return {"status": "ok"}
