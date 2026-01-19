from app.services.mcp_tools import check_doctor_availability, book_appointment, get_appointment_stats, list_doctors, send_doctor_notification

# Tool Schemas for OpenAI/LLM
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "check_doctor_availability",
            "description": "Check available appointment slots for a doctor on a specific date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_name": {
                        "type": "string",
                        "description": "The name of the doctor (e.g. 'Dr. Ahuja')"
                    },
                    "date": {
                        "type": "string",
                        "description": "The date to check in YYYY-MM-DD format (e.g. '2026-01-20')"
                    },
                    "time_preference": {
                        "type": "string",
                        "description": "Optional preference like 'morning', 'afternoon' (not strictly used by logic yet but helpful context)"
                    }
                },
                "required": ["doctor_name", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book a new appointment for a patient. USE THIS tool whenever a user provides booking details (email, date, reason) OR asks for an email confirmation. It automatically sends the Email and Calendar invite.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_id": {
                        "type": "integer",
                        "description": "The ID of the doctor (obtained from check_doctor_availability)"
                    },
                    "patient_name": {
                        "type": "string",
                        "description": "Full name of the patient"
                    },
                    "patient_email": {
                        "type": "string",
                        "description": "Email address of the patient"
                    },
                    "appointment_time": {
                        "type": "string",
                        "description": "The exact ISO timestamp for the appointment (e.g. '2026-01-20T10:00:00'. Obtained from check_doctor_availability slots)"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the visit (e.g. 'Fever', 'Routine Checkup')"
                    }
                },
                "required": ["doctor_id", "patient_name", "patient_email", "appointment_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_appointment_stats",
            "description": "Get appointment statistics and summary for a doctor.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_name": {
                        "type": "string",
                        "description": "The name of the doctor"
                    },
                    "query_type": {
                        "type": "string",
                        "enum": ["today", "tomorrow", "yesterday", "this_week", "daily", "weekly"],
                        "description": "The time period to query stats for. (User friendly options: daily, weekly)"
                    },
                    "filter_by": {
                        "type": "string",
                        "description": "Optional keyword to filter by reason (e.g. 'fever')"
                    }
                },
                "required": ["doctor_name", "query_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_doctors",
            "description": "List all registered doctors and their IDs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "specialization": {
                        "type": "string",
                        "description": "Optional specialization to filter doctors by (e.g. 'Cardiologist', 'Dentist')."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_doctor_notification",
            "description": "Send a notification to a doctor via Slack/External Channel.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_name": {
                        "type": "string",
                        "description": "Name of the doctor to notify."
                    },
                    "message": {
                        "type": "string",
                        "description": " The message content to send."
                    }
                },
                "required": ["doctor_name", "message"]
            }
        }
    }
]

# Mapping string names to actual functions
AVAILABLE_TOOLS = {
    "check_doctor_availability": check_doctor_availability,
    "book_appointment": book_appointment,
    "get_appointment_stats": get_appointment_stats,
    "list_doctors": list_doctors,
    "send_doctor_notification": send_doctor_notification
}
