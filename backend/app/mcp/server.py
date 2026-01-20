"""
MCP Server for Doctor Appointment Assistant

This module implements a Model Context Protocol (MCP) compliant server
that exposes appointment booking tools for LLM agent orchestration.

The server wraps existing business logic from app.services.mcp_tools
and provides formal MCP tool discovery and invocation capabilities.
"""

import asyncio
import json
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.stdio import stdio_server

from app.services.mcp_tools import (
    check_doctor_availability,
    book_appointment,
    get_appointment_stats,
    list_doctors,
    send_doctor_notification
)

# Initialize MCP Server
server = Server("doctor-appointment-assistant")

# ============================================================================
# TOOL DEFINITIONS (MCP-Compliant)
# ============================================================================

@server.list_tools()
async def list_available_tools() -> list[Tool]:
    """
    MCP Tool Discovery Endpoint
    
    Returns all available tools with their schemas for dynamic LLM discovery.
    This is the core of MCP compliance - tools are discoverable, not hardcoded.
    """
    return [
        Tool(
            name="check_doctor_availability",
            description="Check available appointment slots for a specific doctor on a given date. Returns list of available time slots.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doctor_name": {
                        "type": "string",
                        "description": "Name of the doctor (e.g., 'Dr. Ahuja', 'Dr. Smith')"
                    },
                    "date_str": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format (e.g., '2026-01-21')"
                    },
                    "time_preference": {
                        "type": "string",
                        "description": "Optional time preference like 'morning', 'afternoon', 'evening'"
                    }
                },
                "required": ["doctor_name", "date_str"]
            }
        ),
        Tool(
            name="book_appointment",
            description="Book a new appointment for a patient. Automatically sends email confirmation and creates calendar event. This is the ONLY way to send booking confirmations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doctor_id": {
                        "type": "integer",
                        "description": "ID of the doctor (obtained from check_doctor_availability result)"
                    },
                    "patient_name": {
                        "type": "string",
                        "description": "Full name of the patient"
                    },
                    "patient_email": {
                        "type": "string",
                        "description": "Email address of the patient for confirmation"
                    },
                    "appointment_time_str": {
                        "type": "string",
                        "description": "Appointment datetime in ISO format: YYYY-MM-DDTHH:MM:SS (e.g., '2026-01-21T10:00:00')"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for visit (e.g., 'Fever', 'Checkup', 'Follow-up')"
                    }
                },
                "required": ["doctor_id", "patient_name", "patient_email", "appointment_time_str"]
            }
        ),
        Tool(
            name="get_appointment_stats",
            description="Get appointment statistics and summary for a doctor. Used for generating reports about patient visits.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doctor_name": {
                        "type": "string",
                        "description": "Name of the doctor"
                    },
                    "query_type": {
                        "type": "string",
                        "enum": ["today", "tomorrow", "yesterday", "this_week", "daily", "weekly"],
                        "description": "Time period for the report"
                    },
                    "filter_by": {
                        "type": "string",
                        "description": "Optional filter by reason/condition (e.g., 'fever', 'checkup')"
                    }
                },
                "required": ["doctor_name", "query_type"]
            }
        ),
        Tool(
            name="list_doctors",
            description="List all available doctors with their IDs and specializations. Use this when you need to find a doctor's ID or show available doctors.",
            inputSchema={
                "type": "object",
                "properties": {
                    "specialization": {
                        "type": "string",
                        "description": "Optional filter by specialization (e.g., 'Cardiologist', 'Dentist')"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="send_doctor_notification",
            description="Send a notification to a doctor via Slack. Used for urgent messages or report delivery.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doctor_name": {
                        "type": "string",
                        "description": "Name of the doctor to notify"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message content to send"
                    },
                    "channel": {
                        "type": "string",
                        "description": "Notification channel (default: 'slack')"
                    }
                },
                "required": ["doctor_name", "message"]
            }
        )
    ]


# ============================================================================
# TOOL IMPLEMENTATIONS (MCP Call Handlers)
# ============================================================================

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """
    MCP Tool Invocation Handler
    
    This is called by the LLM agent when it decides to use a tool.
    It routes to the appropriate business logic function and returns results.
    """
    
    # Route to appropriate tool function
    if name == "check_doctor_availability":
        result = await check_doctor_availability(
            doctor_name=arguments.get("doctor_name"),
            date_str=arguments.get("date_str"),
            time_preference=arguments.get("time_preference")
        )
    
    elif name == "book_appointment":
        result = await book_appointment(
            doctor_id=arguments.get("doctor_id"),
            patient_name=arguments.get("patient_name"),
            patient_email=arguments.get("patient_email"),
            appointment_time_str=arguments.get("appointment_time_str"),
            reason=arguments.get("reason")
        )
    
    elif name == "get_appointment_stats":
        result = await get_appointment_stats(
            doctor_name=arguments.get("doctor_name"),
            query_type=arguments.get("query_type"),
            filter_by=arguments.get("filter_by")
        )
    
    elif name == "list_doctors":
        result = await list_doctors(
            specialization=arguments.get("specialization")
        )
    
    elif name == "send_doctor_notification":
        result = await send_doctor_notification(
            doctor_name=arguments.get("doctor_name"),
            message=arguments.get("message"),
            channel=arguments.get("channel", "slack")
        )
    
    else:
        result = {"error": f"Unknown tool: {name}"}
    
    # Return as MCP TextContent
    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2, default=str)
    )]


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

async def main():
    """Run the MCP server using stdio transport"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
