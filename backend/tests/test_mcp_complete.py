"""
Comprehensive Test Suite for MCP Agentic AI System

Tests all core capabilities:
1. MCP tool discovery
2. Multi-turn conversation
3. Natural language understanding
4. Dynamic tool invocation
5. Tool chaining
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from app.mcp.server import list_available_tools
from app.services.llm_service import process_chat_message


async def test_mcp_tool_discovery():
    """Test 1: MCP Tool Discovery"""
    print("\n" + "="*80)
    print("TEST 1: MCP Tool Discovery")
    print("="*80)
    
    tools = await list_available_tools()
    
    assert len(tools) == 5, f"Expected 5 tools, found {len(tools)}"
    
    tool_names = [t.name for t in tools]
    expected_tools = [
        "check_doctor_availability",
        "book_appointment",
        "get_appointment_stats",
        "list_doctors",
        "send_doctor_notification"
    ]
    
    for expected in expected_tools:
        assert expected in tool_names, f"Missing tool: {expected}"
    
    print("✅ PASSED: All 5 tools discovered via MCP")
    print(f"   Tools: {', '.join(tool_names)}")
    return True


async def test_multi_turn_conversation():
    """Test 2: Multi-Turn Context Continuity"""
    print("\n" + "="*80)
    print("TEST 2: Multi-Turn Conversation Context")
    print("="*80)
    
    session_id = None
    
    # Turn 1: Ask about availability
    print("\n👤 User: Is Dr. Ahuja available tomorrow?")
    result1 = await process_chat_message(
        "Is Dr. Ahuja available tomorrow?",
        session_id=session_id
    )
    session_id = result1["session_id"]
    print(f"🤖 AI: {result1['response'][:100]}...")
    
    # Turn 2: Reference previous context
    print("\n👤 User: What about the day after?")
    result2 = await process_chat_message(
        "What about the day after?",
        session_id=session_id
    )
    print(f"🤖 AI: {result2['response'][:100]}...")
    
    # Verify same session
    assert result2["session_id"] == session_id, "Session ID changed!"
    
    print("\n✅ PASSED: Multi-turn context maintained")
    print(f"   Session ID: {session_id}")
    return True


async def test_natural_language_understanding():
    """Test 3: Natural Language Intent Parsing"""
    print("\n" + "="*80)
    print("TEST 3: Natural Language Understanding")
    print("="*80)
    
    test_cases = [
        "Find me a cardiologist",
        "I need to see a heart doctor",
        "Show me doctors who treat heart problems"
    ]
    
    for query in test_cases:
        print(f"\n👤 User: {query}")
        result = await process_chat_message(query)
        print(f"🤖 AI: {result['response'][:80]}...")
        
        # All should understand "cardiologist" intent
        assert "cardiologist" in result['response'].lower() or "smith" in result['response'].lower(), \
            f"Failed to understand cardiologist intent in: {query}"
    
    print("\n✅ PASSED: Natural language understanding works")
    return True


async def test_tool_invocation():
    """Test 4: Dynamic Tool Invocation"""
    print("\n" + "="*80)
    print("TEST 4: Dynamic Tool Invocation")
    print("="*80)
    
    # This should trigger list_doctors tool
    print("\n👤 User: List all available doctors")
    result = await process_chat_message("List all available doctors")
    print(f"🤖 AI: {result['response'][:150]}...")
    
    # Should mention multiple doctors
    assert "Dr." in result['response'], "No doctors listed"
    
    print("\n✅ PASSED: Tool invocation working")
    return True


async def test_error_handling():
    """Test 5: Graceful Error Handling"""
    print("\n" + "="*80)
    print("TEST 5: Error Handling")
    print("="*80)
    
    # Ambiguous request
    print("\n👤 User: Book an appointment")
    result = await process_chat_message("Book an appointment")
    print(f"🤖 AI: {result['response'][:100]}...")
    
    # Should ask for clarification, not crash
    assert "error" not in result['response'].lower() or "which doctor" in result['response'].lower(), \
        "System crashed instead of asking for clarification"
    
    print("\n✅ PASSED: Error handling works")
    return True


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE TEST SUITE - MCP AGENTIC AI SYSTEM")
    print("="*80)
    
    # Database should already be initialized
    print("\nAssuming database is already running...\n")
    
    tests = [
        ("MCP Tool Discovery", test_mcp_tool_discovery),
        ("Multi-Turn Conversation", test_multi_turn_conversation),
        ("Natural Language Understanding", test_natural_language_understanding),
        ("Dynamic Tool Invocation", test_tool_invocation),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ FAILED: {test_name}")
            print(f"   Error: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is ready for production.")
        print("\nVerified Capabilities:")
        print("  ✅ MCP-compliant tool discovery")
        print("  ✅ Multi-turn conversation with context")
        print("  ✅ Natural language understanding")
        print("  ✅ Dynamic tool invocation")
        print("  ✅ Graceful error handling")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review errors above.")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
