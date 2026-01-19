# MediAssist - Agentic AI Doctor Appointment & Reporting System (Full Stack)

Built with **FastAPI**, **React**, **PostgreSQL**, and **Google Gemini** (Agentic AI with MCP).

## 📌 Project Overview
MediAssist is an intelligent assistant that allows:
1.  **Patients**: To book appointments with specialists via natural language chat ("Find me a Cardiologist and book for 10 AM").
2.  **Doctors**: To receive real-time notifications on Slack and query their schedule ("How many patients do I have today?").

The system uses **Model Context Protocol (MCP)** principles where the AI autonomously discovers and triggers backend tools (Database queries, Google Calendar API, Slack Webhooks).

## 🌟 Key Features
*   **Agentic AI Workflow**: The LLM decides when to search for doctors, check availability, or finalize a booking based on context.
*   **Intelligent Doctor Filtering**: Users can ask for "Heart Specialist" and the AI filters for "Cardiologist" effectively.
*   **Real-time Notifications**: Validated integration with **Slack** for instant doctor alerts.
*   **Google Calendar Sync**: Automatically creates calendar events for booked slots.
*   **Aesthetic UI**: A polished, minimal, and responsive chat interface.
*   **Robust Backend**: Async SQLAlchemy with a self-correcting validation layer.

## 🛠️ Tech Stack
*   **Frontend**: React + Vite (Modern "Floating Card" Chat UI)
*   **Backend**: FastAPI, AsyncPG, SQLAlchemy, Pydantic
*   **AI/LLM**: Google Gemini Flash (via `google-genai` SDK)
*   **Database**: PostgreSQL
*   **Tools/Integrations**: Slack Webhooks, Google Calendar API

## 🚀 Setup Instructions

### 1. Prerequisites
*   Node.js & npm
*   Python 3.10+
*   PostgreSQL (running locally or via Docker)

### 2. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure Environment
# Copy .env.example to .env and add your API keys (Gemini, Slack, DB URL)
```

**Initialize Database & Seed Data:**
```bash
# This applies migrations and seeds 20+ specialist doctors
python scripts/seed_data.py
```

**Run Server:**
```bash
python -m uvicorn app.main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Access the app at: `http://localhost:5173`

## 📖 Usage Scenarios

### Scenario 1: Patient Booking
1.  **User**: "Find me a Cardiologist."
    *   **System**: Lists Dr. Sarah Smith (Cardiologist).
2.  **User**: "Book an appointment with her for tomorrow at 10 AM."
    *   **System**: Checks DB for 10:00 AM slot -> Books it -> Sends Slack Notification -> Confirms to user.

### Scenario 2: Doctor Reporting
1.  **Doctor (via Chat)**: "How many appointments do I have today?"
    *   **System**: Queries DB for today's count -> Returns summary.

## 🧪 Testing
The project includes a robust set of 20 seeded doctors including:
*   **Dr. Sarah Smith** (Cardiologist)
*   **Dr. Michael Molar** (Dentist)
*   **Dr. Robert Chen** (Neurologist)
...and more.

## Note on Architecture
*   **Authentication**: Simplified for "One-Page" access as per user requirements (Guest ID: 1).
*   **Notifications**: Currently configured for Slack (Webhook).
