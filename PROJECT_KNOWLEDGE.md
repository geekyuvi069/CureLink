# 🧠 MediAssist Project Knowledge Base

This document serves as the "source of truth" for the MediAssist project, capturing architectural decisions, implementation details, and operational workflows.

## 🌟 System Purpose
MediAssist is an Agentic AI-powered healthcare assistant designed to streamline doctor appointment bookings and administrative reporting through a natural language interface.

---

## 🏗️ Core Architecture

### 1. Agentic AI Layer
- **Engine**: Google Gemini Flash (via `google-genai` SDK).
- **Behavior**: Autonomous reasoning loop that parses user intent, extracts entities, and chains backend tools.
- **Context Management**: Multi-turn conversation persistence using PostgreSQL-backed `ConversationSession` (found in `app.models.models`).

### 2. Model Context Protocol (MCP)
- **Protocol**: Formal implementation of MCP for tool discovery and execution.
- **Server**: `app/mcp/server.py` exposes formal tool schemas.
- **Tools Discovery**: The agent dynamically lists and selects tools at runtime, moving away from hardcoded function mappings.

### 3. Backend Stack
- **Framework**: FastAPI (Async).
- **ORM**: SQLAlchemy 2.0 (Async).
- **Database**: PostgreSQL (via `asyncpg`).
- **Scheduling**: Integration with Google Calendar API.
- **Notifications**: Slack Block Kit (Premium formatting) and SMTP/Gmail.

---

## 📂 Key Files Directory

| Path | Purpose |
| :--- | :--- |
| `backend/app/mcp/server.py` | **The Core**: Formal MCP server implementation for tool discovery. |
| `backend/app/services/llm_service.py` | **The Brain**: Gemini orchestration, reasoning loop, and context management. |
| `backend/app/services/mcp_tools.py` | **The Hands**: Business logic for DB, Google Cal, Email, and Slack. |
| `backend/app/core/tools.py` | Legacy tool schemas (kept for system prompt guidance). |
| `backend/ARCHITECTURE.md` | Detailed architectural diagrams and flow explanations. |
| `backend/scripts/demo_agent_flow.py` | Automated demo script showing agentic behavior. |
| `backend/tests/test_mcp_complete.py` | Comprehensive test suite for MCP compliance. |

---

## 🔒 Security & Environment

### Sensitive Data Management
- **Never commit `.env`**: Contains Gemini API keys, Slack tokens, and DB credentials.
- **Tracked `.gitignore`**: Specifically ignores `token.json`, `credentials.json`, `venv/`, and `.env`.
- **Reference**: Use `.env.example` as a template for new deployments.

### Required Environment Variables
- `DATABASE_URL`: PostgreSQL connection string.
- `GEMINI_API_KEY`: Google AI Studio key.
- `SLACK_BOT_TOKEN` & `SLACK_WEBHOOK_URL`: For doctor notifications.
- `SMTP_USER` & `SMTP_PASSWORD`: For patient email confirmations.

---

## 🤖 AI Reasoning Capabilities

### 1. Date Intelligence
The Agent is injected with dynamic "Today's Date" context in every request, allowing it to accurately resolve:
- "Tomorrow" -> Target YYYY-MM-DD.
- "Next monday" -> Correct calendar date computation.

### 2. Fuzzy Matching
- **Doctor Names**: Maps "Dr. Smith" to "Dr. Sarah Smith" via partial name matching.
- **Specializations**: Maps "heart doctor" to "Cardiologist", "tooth" to "Dentist", etc.

### 3. Slot Awareness
The agent automatically checks availability before booking. If a slot is taken (e.g., 10:00 AM), it proactively suggests the next available slots.

---

## 🧪 Operational Workflows

### Manual Testing
1. **MCP Discovery Check**: `cd backend && python3 -c "from app.mcp.server import ..."`
2. **Full Agent Demo**: `python3 backend/scripts/demo_agent_flow.py`
3. **Automated Verification**: `python3 backend/tests/test_mcp_complete.py`

### Slack UI Formatting (Premium)
- Notifications use **Slack Block Kit + Attachments**.
- Colors: Health Green (`#36a64f`) for the sidebar.
- Layout: Header -> Introduction -> Bulleted List (•) -> Context Footer.

---

## 🛤️ Evolution History (Recent Changes)
1. **MCP Refactor**: Decoupled tool logic into a formal protocol-compliant server.
2. **Date Context Fix**: Injected current time into LLM system instruction to fix "2024 dates" bug.
3. **Fuzzy Expansion**: Added mapping for 12+ common medical terms (brain, skin, child, etc.).
4. **Premium Slack UI**: Upgraded notifications from plain text to high-end Block Kit cards.
5. **Security Audit**: Removed hardcoded Slack secrets and secured `.gitignore` for Google API files.

---

*This document should be updated as the system evolves to ensure context is never lost.*
