#!/bin/bash
# Quick Test Script - Run all tests before deployment

echo "=================================="
echo "🧪 PRE-DEPLOYMENT TEST SUITE"
echo "=================================="
echo ""

# Test 1: MCP Tool Discovery
echo "Test 1: MCP Tool Discovery"
echo "--------------------------"
cd /home/geekyuvi/Desktop/fsd_assesment/backend
python3 -c "
import asyncio
from app.mcp.server import list_available_tools

async def test():
    tools = await list_available_tools()
    print(f'✅ Found {len(tools)} tools:')
    for tool in tools:
        print(f'  - {tool.name}')
    assert len(tools) == 5, 'Expected 5 tools'
    print('')
    print('✅ PASSED: MCP Tool Discovery')

asyncio.run(test())
" || { echo "❌ FAILED: MCP Tool Discovery"; exit 1; }

echo ""
echo "Test 2: Check All New Files Exist"
echo "----------------------------------"
FILES=(
    "app/mcp/__init__.py"
    "app/mcp/server.py"
    "ARCHITECTURE.md"
    "scripts/demo_agent_flow.py"
    "tests/test_mcp_complete.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

echo ""
echo "Test 3: Check Dependencies"
echo "--------------------------"
if grep -q "mcp" requirements.txt; then
    echo "✅ MCP dependency in requirements.txt"
else
    echo "❌ MCP dependency missing"
    exit 1
fi

echo ""
echo "Test 4: Verify Backend Starts"
echo "------------------------------"
timeout 5 python3 -c "
from app.main import app
print('✅ Backend imports successfully')
" || { echo "❌ Backend import failed"; exit 1; }

echo ""
echo "=================================="
echo "✅ ALL PRE-DEPLOYMENT TESTS PASSED"
echo "=================================="
echo ""
echo "System is ready for deployment!"
echo ""
echo "Next steps:"
echo "1. Start backend: cd backend && uvicorn app.main:app --reload"
echo "2. Start frontend: cd frontend && npm run dev"
echo "3. Test in browser: http://localhost:5173"
