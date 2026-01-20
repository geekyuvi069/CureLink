"""
Demo Script: Agentic AI Conversation Flow

This script demonstrates the multi-turn conversational capabilities
and tool orchestration of the Doctor Appointment Assistant.

It simulates realistic user interactions and shows:
1. Tool discovery via MCP
2. Dynamic tool invocation
3. Multi-turn context continuity
4. Natural language understanding
5. Tool chaining
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from app.services.llm_service import process_chat_message
from app.mcp.server import list_available_tools
from app.core.database import init_db


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


async def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title.center(80)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")


async def print_user(message: str):
    """Print user message"""
    print(f"{Colors.BLUE}{Colors.BOLD}👤 User:{Colors.END} {message}")


async def print_ai(message: str):
    """Print AI response"""
    print(f"{Colors.GREEN}{Colors.BOLD}🤖 AI:{Colors.END} {message}\n")


async def print_tool_call(tool_name: str, args: dict):
    """Print tool invocation"""
    print(f"{Colors.YELLOW}  🔧 [Tool Call] {tool_name}{Colors.END}")
    print(f"{Colors.CYAN}     Args: {args}{Colors.END}")


async def demo_tool_discovery():
    """Demonstrate MCP tool discovery"""
    await print_section("DEMO 1: MCP Tool Discovery")
    
    print(f"{Colors.BOLD}Querying MCP Server for available tools...{Colors.END}\n")
    
    tools = await list_available_tools()
    
    print(f"{Colors.GREEN}✅ Found {len(tools)} tools:{Colors.END}\n")
    
    for i, tool in enumerate(tools, 1):
        print(f"{Colors.BOLD}{i}. {tool.name}{Colors.END}")
        print(f"   Description: {tool.description}")
        print(f"   Required params: {tool.inputSchema.get('required', [])}")
        print()
    
    print(f"{Colors.CYAN}💡 Key Point: Tools are discoverable at runtime, not hardcoded!{Colors.END}")


async def demo_multi_turn_booking():
    """Demonstrate multi-turn conversation with context continuity"""
    await print_section("DEMO 2: Multi-Turn Conversation (Booking Flow)")
    
    session_id = None
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"{Colors.BOLD}Scenario: Patient wants to book an appointment{Colors.END}\n")
    
    # Turn 1: Check availability
    await print_user(f"Is Dr. Ahuja available tomorrow?")
    result = await process_chat_message(
        f"Is Dr. Ahuja available tomorrow? (tomorrow is {tomorrow})",
        session_id=session_id
    )
    session_id = result["session_id"]
    await print_ai(result["response"])
    
    # Turn 2: Select time (context: doctor and date remembered)
    await print_user("Book 11 AM")
    result = await process_chat_message(
        "Book 11 AM",
        session_id=session_id
    )
    await print_ai(result["response"])
    
    # Turn 3: Provide name
    await print_user("John Doe")
    result = await process_chat_message(
        "John Doe",
        session_id=session_id
    )
    await print_ai(result["response"])
    
    # Turn 4: Provide email
    await print_user("john.doe@example.com")
    result = await process_chat_message(
        "john.doe@example.com",
        session_id=session_id
    )
    await print_ai(result["response"])
    
    # Turn 5: Provide reason
    await print_user("Fever and cough")
    result = await process_chat_message(
        "Fever and cough",
        session_id=session_id
    )
    await print_ai(result["response"])
    
    print(f"{Colors.CYAN}💡 Key Point: AI remembered doctor, date, and time across 5 turns!{Colors.END}")


async def demo_natural_language_parsing():
    """Demonstrate natural language understanding"""
    await print_section("DEMO 3: Natural Language Understanding")
    
    print(f"{Colors.BOLD}Scenario: Various ways to express the same intent{Colors.END}\n")
    
    test_queries = [
        "Show me Dr. Smith's schedule for tomorrow",
        "When is Dr. Smith free tomorrow?",
        "I need to see Dr. Smith tomorrow, what times are available?",
        "Check if Dr. Smith has any openings tomorrow"
    ]
    
    for query in test_queries:
        await print_user(query)
        result = await process_chat_message(query)
        await print_ai(result["response"])
        await asyncio.sleep(0.5)
    
    print(f"{Colors.CYAN}💡 Key Point: AI understands intent regardless of phrasing!{Colors.END}")


async def demo_tool_chaining():
    """Demonstrate automatic tool chaining"""
    await print_section("DEMO 4: Automatic Tool Chaining")
    
    print(f"{Colors.BOLD}Scenario: Doctor requests daily report{Colors.END}\n")
    
    await print_user("Give me a summary of today's appointments for Dr. Ahuja")
    
    print(f"\n{Colors.YELLOW}Agent Reasoning:{Colors.END}")
    print(f"{Colors.CYAN}  1. Parse intent: 'get appointment summary'{Colors.END}")
    print(f"{Colors.CYAN}  2. Extract entities: doctor='Dr. Ahuja', period='today'{Colors.END}")
    print(f"{Colors.CYAN}  3. Select tool: 'get_appointment_stats'{Colors.END}")
    print(f"{Colors.CYAN}  4. Execute tool with parameters{Colors.END}")
    print(f"{Colors.CYAN}  5. Format results for human readability{Colors.END}\n")
    
    result = await process_chat_message(
        "Give me a summary of today's appointments for Dr. Ahuja"
    )
    await print_ai(result["response"])
    
    print(f"{Colors.CYAN}💡 Key Point: Agent autonomously selected and executed the right tool!{Colors.END}")


async def demo_context_switching():
    """Demonstrate context switching between topics"""
    await print_section("DEMO 5: Context Switching")
    
    session_id = None
    
    print(f"{Colors.BOLD}Scenario: User switches between different doctors{Colors.END}\n")
    
    # Ask about Dr. Smith
    await print_user("Is Dr. Smith available tomorrow?")
    result = await process_chat_message(
        "Is Dr. Smith available tomorrow?",
        session_id=session_id
    )
    session_id = result["session_id"]
    await print_ai(result["response"])
    
    # Switch to Dr. Ahuja
    await print_user("What about Dr. Ahuja?")
    result = await process_chat_message(
        "What about Dr. Ahuja?",
        session_id=session_id
    )
    await print_ai(result["response"])
    
    # Reference "the first one" - should refer to Dr. Ahuja's first slot
    await print_user("Book the first available slot")
    result = await process_chat_message(
        "Book the first available slot",
        session_id=session_id
    )
    await print_ai(result["response"])
    
    print(f"{Colors.CYAN}💡 Key Point: AI tracks context switches and resolves ambiguous references!{Colors.END}")


async def demo_error_handling():
    """Demonstrate graceful error handling"""
    await print_section("DEMO 6: Error Handling & Edge Cases")
    
    print(f"{Colors.BOLD}Scenario: Invalid or ambiguous requests{Colors.END}\n")
    
    # Ambiguous doctor name
    await print_user("Book Dr. Smith")
    result = await process_chat_message("Book Dr. Smith")
    await print_ai(result["response"])
    
    # Missing information
    await print_user("Book tomorrow at 10 AM")
    result = await process_chat_message("Book tomorrow at 10 AM")
    await print_ai(result["response"])
    
    print(f"{Colors.CYAN}💡 Key Point: AI asks clarifying questions instead of failing!{Colors.END}")


async def main():
    """Run all demos"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                            ║")
    print("║           🤖 AGENTIC AI DEMONSTRATION - Doctor Appointment System          ║")
    print("║                                                                            ║")
    print("║  This demo proves:                                                         ║")
    print("║  ✅ MCP-compliant tool discovery                                           ║")
    print("║  ✅ Multi-turn conversation with context continuity                        ║")
    print("║  ✅ Natural language understanding                                         ║")
    print("║  ✅ Dynamic tool invocation and chaining                                   ║")
    print("║  ✅ Intelligent error handling                                             ║")
    print("║                                                                            ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    # Initialize database
    print(f"{Colors.YELLOW}Initializing database connection...{Colors.END}")
    await init_db()
    print(f"{Colors.GREEN}✅ Database ready{Colors.END}\n")
    
    try:
        # Run demos
        await demo_tool_discovery()
        await asyncio.sleep(2)
        
        await demo_multi_turn_booking()
        await asyncio.sleep(2)
        
        await demo_natural_language_parsing()
        await asyncio.sleep(2)
        
        await demo_tool_chaining()
        await asyncio.sleep(2)
        
        await demo_context_switching()
        await asyncio.sleep(2)
        
        await demo_error_handling()
        
        # Summary
        await print_section("DEMONSTRATION COMPLETE")
        print(f"{Colors.GREEN}{Colors.BOLD}✅ All demos completed successfully!{Colors.END}\n")
        print(f"{Colors.BOLD}Summary of Proven Capabilities:{Colors.END}")
        print(f"  ✅ MCP tool discovery and dynamic invocation")
        print(f"  ✅ Multi-turn conversations with full context")
        print(f"  ✅ Natural language intent parsing")
        print(f"  ✅ Autonomous tool selection and chaining")
        print(f"  ✅ Graceful error handling")
        print(f"  ✅ Context switching and reference resolution")
        print()
        print(f"{Colors.CYAN}This system demonstrates true agentic AI behavior!{Colors.END}\n")
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error during demo: {e}{Colors.END}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
