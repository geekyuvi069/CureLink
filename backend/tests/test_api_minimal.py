
import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai

async def test_gemini():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env")
        return
    
    print(f"Testing Gemini with key: {api_key[:10]}...")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    try:
        response = model.generate_content("Hello, are you there?")
        print(f"Response: {response.text}")
        print("Gemini connectivity: SUCCESS")
    except Exception as e:
        print(f"Gemini connectivity: FAILED")
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini())
