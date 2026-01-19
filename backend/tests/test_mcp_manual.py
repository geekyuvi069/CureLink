import asyncio
import sys
import os
from datetime import date, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from app.services.mcp_tools import check_doctor_availability, book_appointment, get_appointment_stats

async def test_tools():
    print("--- Testing MCP Tools ---")

    # 1. Find next Monday
    today = date.today()
    days_ahead = 0 - today.weekday() # If today is Monday(0), 0 days ahead. If Tue(1), -1... wait, we want NEXT monday if passed.
    if days_ahead <= 0: 
        days_ahead += 7
    next_monday = today + timedelta(days=days_ahead)
    date_str = next_monday.strftime("%Y-%m-%d")
    
    print(f"\n1. Checking availability for Dr. Ahuja on {date_str} (Monday)...")
    avail = await check_doctor_availability("Ahuja", date_str)
    print(avail)

    if "available_slots" in avail and avail["available_slots"]:
        first_slot = avail["available_slots"][0]
        print(f"\n2. Booking slot: {first_slot}")
        
        # ISO format: YYYY-MM-DDTHH:MM:SS
        appt_time = f"{date_str}T{first_slot}:00"
        
        booking = await book_appointment(
            doctor_id=avail["doctor_id"],
            patient_name="John Doe",
            patient_email="john@example.com",
            appointment_time_str=appt_time,
            reason="Fever checkup"
        )
        print(booking)

        print("\n3. Checking availability again (slot should be gone)...")
        avail_after = await check_doctor_availability("Ahuja", date_str)
        print(f"Slots: {avail_after.get('available_slots')}")

    print("\n4. Getting stats for 'appointment' week...")
    # Since we booked it for next monday, let's just query by doctor name and ensure no errors
    stats = await get_appointment_stats("Ahuja", "this_week") 
    # Note: 'this_week' logic in code assumes current calendar week. If next monday is next week, it won't show.
    # Let's try querying for that specific day if I added a 'specific_day' filter, but the tool only supports 'today','tomorrow', etc.
    # For testing, let's just print what we get.
    print(stats)

if __name__ == "__main__":
    asyncio.run(test_tools())
