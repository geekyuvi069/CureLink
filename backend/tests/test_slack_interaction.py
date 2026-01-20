import httpx
import asyncio
import json
import hmac
import hashlib
import time
import os

# Try to load the secret from .env if available, or use a default for testing
# Try to load the secret from env
from app.core.config import settings
SLACK_SIGNING_SECRET = settings.SLACK_SIGNING_SECRET
if not SLACK_SIGNING_SECRET:
    print("Warning: SLACK_SIGNING_SECRET not set. Using dummy value for test generation, but backend verification might fail if configured with a different secret.")
    SLACK_SIGNING_SECRET = "dummy_secret_for_testing"

async def test_mock_slack_event():
    url = "http://localhost:8000/api/slack/events"
    
    # Mock Slack app_mention event
    payload_dict = {
        "token": "verification_token",
        "team_id": "T01234567",
        "api_app_id": "A01234567",
        "event": {
            "type": "app_mention",
            "user": "U12345678",
            "text": "<@U01234567> give me a summary of today's appointments",
            "ts": f"{time.time()}",
            "channel": "C12345678",
            "event_ts": f"{time.time()}"
        },
        "type": "event_callback",
        "event_id": "Ev01234567",
        "event_time": int(time.time())
    }
    
    body_str = json.dumps(payload_dict)
    timestamp = str(int(time.time()))
    
    # Generate signature
    sig_basestring = f"v0:{timestamp}:{body_str}"
    signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode("utf-8"),
        sig_basestring.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        "X-Slack-Request-Timestamp": timestamp,
        "X-Slack-Signature": signature,
        "Content-Type": "application/json"
    }
    
    print(f"Sending mock Slack event to {url}...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, content=body_str, headers=headers)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
            
            if response.status_code == 200:
                print("\nSuccess! The endpoint processed the event.")
                print("Check your backend logs to see if Gemini was called and if it tried to respond.")
            else:
                print(f"\nFailed. Status: {response.status_code}")
                print("Make sure the backend server is running on http://localhost:8000")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_mock_slack_event())
