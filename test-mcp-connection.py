#!/usr/bin/env python3
"""
Test MCP Server Connection and Data Reception
"""
import asyncio
import httpx
import json
import sys

async def test_mcp_server():
    """Test MCP server endpoints"""
    base_url = "http://localhost:3001"
    
    print("🔍 Testing MCP Server Connection...")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing Health Endpoint:")
    print(f"   URL: {base_url}/health")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Health: {result}")
            else:
                print(f"   ❌ Health Status: {response.status_code}")
                print(f"   📄 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Health Error: {e}")
        print(f"   🔍 Check if MCP server is running on port 3001")
    
    # Test 2: List Tools
    print("\n2. Testing Tools List:")
    print(f"   URL: {base_url}/list_tools")
    try:
        async with httpx.AsyncClient(timeout=6000.0) as client:
            response = await client.get(f"{base_url}/list_tools")
            if response.status_code == 200:
                data = response.json()
                tools = data.get("tools", [])
                print(f"   ✅ Found {len(tools)} tools:")
                for i, tool in enumerate(tools, 1):
                    print(f"      {i}. {tool.get('name', 'Unknown')} - {tool.get('description', 'No description')[:50]}...")
            else:
                print(f"   ❌ Tools Status: {response.status_code}")
                print(f"   📄 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Tools Error: {e}")
    
    # Test 3: Tool Call - Performance Analysis
    print("\n3. Testing Performance Analysis Tool:")
    print(f"   URL: {base_url}/call_tool")
    print(f"   Tool: get_website_performance")
    print(f"   Arguments: {json.dumps({'url': 'https://nike.com', 'strategy': 'desktop'}, indent=6)}")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "name": "get_website_performance",
                "arguments": {
                    "url": "https://nike.com",
                    "strategy": "desktop"
                }
            }
            response = await client.post(
                f"{base_url}/call_tool",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"   📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Tool Call Success")
                content = result.get("content", [])
                if content and len(content) > 0:
                    text = content[0].get("text", "")
                    if text:
                        try:
                            data = json.loads(text)
                            score = data.get('performance_score', 0)
                            url = data.get('url', 'Unknown')
                            print(f"   📈 Performance Score: {score}/100 for {url}")
                            print(f"   📄 Full Response: {text[:200]}...")
                        except json.JSONDecodeError:
                            print(f"   📄 Response: {text[:200]}...")
                else:
                    print(f"   📄 Response: {json.dumps(result, indent=6)[:200]}...")
            else:
                print(f"   ❌ Tool Call Status: {response.status_code}")
                print(f"   📄 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Tool Call Error: {e}")
        print(f"   🔍 Check API keys and network connection")
    
    # Test 4: Tool Call - Uptime Check
    print("\n4. Testing Uptime Check Tool:")
    print(f"   URL: {base_url}/call_tool")
    print(f"   Tool: get_website_uptime")
    print(f"   Arguments: {json.dumps({'url': 'https://google.com', 'friendly_name': 'Google'}, indent=6)}")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "name": "get_website_uptime",
                "arguments": {
                    "url": "https://google.com",
                    "friendly_name": "Google"
                }
            }
            response = await client.post(
                f"{base_url}/call_tool",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"   📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Uptime Check Success")
                content = result.get("content", [])
                if content and len(content) > 0:
                    text = content[0].get("text", "")
                    print(f"   📄 Response: {text[:200]}...")
            else:
                print(f"   ❌ Uptime Check Status: {response.status_code}")
                print(f"   📄 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Uptime Check Error: {e}")
        print(f"   🔍 Check UptimeRobot API key")
    
    # Test 5: Root Endpoint
    print("\n5. Testing Root Endpoint:")
    print(f"   URL: {base_url}/")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Root Endpoint: {result.get('service', 'Unknown')} v{result.get('version', 'Unknown')}")
                endpoints = result.get('endpoints', {})
                print(f"   🔗 Available endpoints: {list(endpoints.keys())}")
            else:
                print(f"   ❌ Root Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Root Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Test Complete!")
    print("\n📋 Summary:")
    print("   ✅ Health Check: Server availability")
    print("   ✅ Tools List: Available functions")
    print("   ✅ Performance Tool: Google PageSpeed API")
    print("   ✅ Uptime Tool: UptimeRobot API")
    print("   ✅ Root Endpoint: Service info")
    print("\n🔍 If any test failed, check:")
    print("   • MCP server is running: npm run dev (in mcp-server folder)")
    print("   • Port 3001 is available")
    print("   • API keys are set in .env file")
    print("   • Network connection to external APIs")

async def test_backend_connection():
    """Test backend to MCP server connection"""
    print("\n🔗 Testing Backend to MCP Server Connection...")
    print("=" * 60)
    
    backend_url = "http://localhost:8000"
    
    # Test Backend Health
    print("\n1. Testing Backend Health:")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{backend_url}/health")
            if response.status_code == 200:
                result = response.json()
                mcp_status = result.get('mcp_server', 'unknown')
                print(f"   ✅ Backend Health: {result.get('status', 'unknown')}")
                print(f"   🔗 MCP Server Status: {mcp_status}")
            else:
                print(f"   ❌ Backend Health: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend Error: {e}")
        print(f"   🔍 Check if backend is running on port 8000")
    
    # Test Backend Status
    print("\n2. Testing Backend Detailed Status:")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{backend_url}/status")
            if response.status_code == 200:
                result = response.json()
                backend_info = result.get('backend', {})
                mcp_info = result.get('mcp_server', {})
                print(f"   ✅ Backend: {backend_info.get('status', 'unknown')} v{backend_info.get('version', 'unknown')}")
                print(f"   🔗 MCP Server: {mcp_info.get('status', 'unknown')} at {mcp_info.get('url', 'unknown')}")
                print(f"   🛠️  Available Tools: {mcp_info.get('tools_count', 0)}")
            else:
                print(f"   ❌ Backend Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend Status Error: {e}")
    
    print("\n" + "=" * 60)

async def main():
    """Main test function"""
    try:
        # Test MCP server directly
        await test_mcp_server()
        
        # Test backend to MCP connection
        await test_backend_connection()
        
        print("\n🎉 All tests completed!")
        print("\n📝 Next Steps:")
        print("   1. If MCP tests pass: MCP server is working correctly")
        print("   2. If backend tests pass: Backend can connect to MCP")
        print("   3. If both pass: Full system is ready")
        print("   4. Test full flow: curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{\"messages\":[{\"content\":\"analyze nike.com\"}]}'")
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())