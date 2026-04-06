import asyncio
import logging
import os
import sys
import json
import re
from typing import Dict, Any
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('marketing_agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Marketing Agent Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    messages: list
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str

class MCPClient:
    def __init__(self):
        self.base_url = f"http://{os.getenv('MCP_SERVER_HOST', 'localhost')}:{os.getenv('MCP_SERVER_PORT', '3001')}"
        self.timeout = httpx.Timeout(6000.0)  # Match MCP server: 6000000ms = 100 minutes
        logger.info(f"MCP Client initialized with base URL: {self.base_url}")
    
    async def is_server_available(self) -> bool:
        """Check if MCP server is available"""
        logger.info(f"Checking MCP server availability at: {self.base_url}/health")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:  # Increased to 30 seconds for health checks
                response = await client.get(f"{self.base_url}/health")
                logger.info(f"MCP Health Check Status: {response.status_code}")
                logger.info(f"MCP Health Check Response: {response.text}")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"MCP server unavailable: {str(e)}")
            logger.error(f"Failed to connect to: {self.base_url}/health")
            return False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool directly"""
        logger.info(f"Calling MCP tool: {tool_name} with arguments: {arguments}")
        logger.info(f"MCP Server Base URL: {self.base_url}")
        logger.info(f"MCP Tool Endpoint: {self.base_url}/call_tool")
        
        # Check if server is available first
        if not await self.is_server_available():
            error_msg = "MCP server is not available. Please ensure that MCP server is running on port 3001."
            logger.error(f"MCP Tool Error: {error_msg}")
            return {"error": error_msg}
        
        try:
            endpoint_url = f"{self.base_url}/call_tool"
            logger.info(f"Making POST request to: {endpoint_url}")
            logger.info(f"Request payload: {json.dumps({'name': tool_name, 'arguments': arguments}, indent=2)}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    endpoint_url,
                    json={"name": tool_name, "arguments": arguments},
                    headers={"Content-Type": "application/json"}
                )
                logger.info(f"MCP Response Status: {response.status_code}")
                logger.info(f"MCP Response Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"MCP Tool Success: {tool_name}")
                    logger.info(f"MCP Response Data: {json.dumps(result, indent=2)}")
                    return result
                else:
                    error_msg = f"MCP call failed: {response.status_code} - {response.text}"
                    logger.error(f"MCP Tool Error: {error_msg}")
                    logger.error(f"MCP Response Body: {response.text}")
                    return {"error": error_msg}
        except Exception as e:
            error_msg = f"MCP call exception: {str(e)}"
            logger.error(f"MCP Tool Exception: {error_msg}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {"error": error_msg}
    
    async def list_tools(self) -> list:
        """List available MCP tools"""
        logger.info("Requesting MCP tools list")
        
        # Check if server is available first
        if not await self.is_server_available():
            logger.error("MCP server unavailable - cannot list tools")
            return []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/list_tools")
                logger.info(f"MCP List Tools Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    tools = data.get("tools", [])
                    logger.info(f"MCP Tools Found: {len(tools)} tools")
                    for tool in tools:
                        logger.info(f"  Tool {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                    return tools
                else:
                    error_msg = f"MCP list tools failed: {response.status_code}"
                    logger.error(f"MCP List Tools Error: {error_msg}")
                    raise Exception(error_msg)
        except Exception as e:
            error_msg = f"MCP list tools exception: {str(e)}"
            logger.error(f"MCP List Tools Exception: {error_msg}")
            return []

class GrokClient:
    """Groq API client for LLM support"""
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.base_url = "https://api.groq.com/openai/v1"
        self.timeout = httpx.Timeout(30.0)
        logger.info(f"Grok Client initialized with API key: {'✓' if self.api_key else '✗'}")
    
    async def query(self, prompt: str, context: str = "") -> str:
        """Query Grok API with context"""
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found - LLM queries will fail")
            return "I apologize, but LLM service is not available. Please set GROQ_API_KEY environment variable."
        
        try:
            system_prompt = """You are a helpful marketing analytics assistant. You have access to web performance and monitoring tools.
            When users ask questions that require analysis beyond simple tool calls, provide helpful insights and recommendations.
            Keep responses concise and actionable."""
            
            full_prompt = f"Context: {context}\n\nUser Question: {prompt}"
            
            logger.info(f"Querying Grok LLM with prompt: {prompt[:100]}...")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json={
                        "model": "llama3-70b-8192",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": full_prompt}
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.7
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = data["choices"][0]["message"]["content"]
                    logger.info(f"Grok LLM response received: {result[:100]}...")
                    return result
                else:
                    error_msg = f"Grok API error: {response.status_code} - {response.text}"
                    logger.error(f"Grok LLM Error: {error_msg}")
                    return f"I apologize, but I encountered an error with the LLM service: {error_msg}"
                    
        except Exception as e:
            error_msg = f"Grok LLM exception: {str(e)}"
            logger.error(f"Grok LLM Exception: {error_msg}")
            return f"I apologize, but I encountered an error with the LLM service: {error_msg}"

class SimpleMarketingAgent:
    def __init__(self):
        self.mcp_client = MCPClient()
        self.grok_client = GrokClient()
        
    async def process_message(self, user_message: str) -> str:
        """Process user message with enhanced logic including LLM support"""
        logger.info(f"Processing user message: '{user_message}'")
        
        message_lower = user_message.lower()
        
        # Check for URLs in the message
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, user_message)
        
        # Define tool-related keywords
        performance_keywords = ['performance', 'speed', 'analyze', 'check', 'test', 'audit']
        uptime_keywords = ['uptime', 'monitor', 'status', 'available', 'down', 'check']
        monitor_keywords = ['create monitor', 'add monitor', 'new monitor', 'setup monitor']
        
        # Simple tool-based queries
        if urls:
            url = urls[0]
            logger.info(f"URL detected: {url}")
            
            # Performance analysis
            if any(keyword in message_lower for keyword in performance_keywords):
                logger.info("Performance analysis requested")
                result = await self.mcp_client.call_tool("get_website_performance", {"url": url})
                if "error" not in result:
                    data = json.loads(result["content"][0]["text"])
                    return f"📊 **Performance Analysis for {url}**\n\n**Performance Score: {data.get('performance_score', 0)}/100**\n\n**Key Metrics:**\n- First Contentful Paint: {data.get('metrics', {}).get('first_contentful_paint', 0):.0f}ms\n- Largest Contentful Paint: {data.get('metrics', {}).get('largest_contentful_paint', 0):.0f}ms\n- Cumulative Layout Shift: {data.get('metrics', {}).get('cumulative_layout_shift', 0):.3f}\n- Total Blocking Time: {data.get('metrics', {}).get('total_blocking_time', 0):.0f}ms\n\n**Top Opportunities:**\n" + "\n".join([f"• {opp.get('title', 'Unknown')}" for opp in data.get('opportunities', [])[:3]])
                else:
                    return f"I apologize, but I encountered an error analyzing the performance of {url}: {result.get('error', 'Unknown error')}"
            
            # Uptime check
            elif any(keyword in message_lower for keyword in uptime_keywords):
                logger.info("Uptime check requested")
                result = await self.mcp_client.call_tool("get_website_uptime", {"url": url, "friendly_name": url})
                if "error" not in result:
                    data = json.loads(result["content"][0]["text"])
                    return f"🔍 **Uptime Check for {url}**\n\n{data}"
                else:
                    return f"I apologize, but I encountered an error checking uptime for {url}: {result.get('error', 'Unknown error')}"
            
            # Create monitor
            elif any(keyword in message_lower for keyword in monitor_keywords):
                logger.info("Monitor creation requested")
                result = await self.mcp_client.call_tool("create_monitor", {"url": url, "friendly_name": url})
                if "error" not in result:
                    data = json.loads(result["content"][0]["text"])
                    return f"📈 **Monitor Created for {url}**\n\n{data}"
                else:
                    return f"I apologize, but I encountered an error creating a monitor for {url}: {result.get('error', 'Unknown error')}"
        
        # Complex queries that need LLM analysis
        complex_keywords = ['why', 'how', 'what', 'explain', 'recommend', 'suggest', 'improve', 'optimize', 'strategy', 'best practices']
        if any(keyword in message_lower for keyword in complex_keywords):
            logger.info("Complex query detected, using LLM")
            
            # Get context from available tools
            context = ""
            if urls:
                context += f"Website URL: {urls[0]}\n"
            
            # Try to get tool results for context
            if urls:
                try:
                    perf_result = await self.mcp_client.call_tool("get_website_performance", {"url": urls[0]})
                    if "error" not in perf_result:
                        context += f"Performance data available for analysis\n"
                except:
                    pass
            
            # Query LLM
            llm_response = await self.grok_client.query(user_message, context)
            return f"🤖 **AI Analysis**\n\n{llm_response}"
        
        # Default response
        return """🚀 **Marketing Agent Ready!**

I can help you with:

📊 **Performance Analysis**
- "Analyze performance of nike.com"
- "Check speed for amazon.com"

🔍 **Uptime Monitoring**
- "Check uptime for google.com"
- "Is facebook.com down?"

📈 **Monitor Creation**
- "Create monitor for tesla.com"
- "Setup monitoring for example.com"

🤖 **AI-Powered Insights**
- "Why is my website slow?"
- "How can I improve page speed?"
- "What are the best practices for web performance?"

Try one of these commands or ask me anything about web performance and monitoring!"""
        
# Initialize the agent
marketing_agent = SimpleMarketingAgent()
                        for opp in opportunities[:3]:  # Top 3 opportunities
                            title = opp.get('title', 'Unknown')
                            impact = opp.get('impact', 0)
                            response += f"• {title} (Impact: {impact:.1f}%)\n"
                    
                    response += f"\n⏰ Analysis completed at: {performance_data.get('timestamp', 'Unknown')}"
                    return response
            
            return "Performance data received but couldn't parse the results."
        except Exception as e:
            logger.error(f"Error formatting performance response: {str(e)}")
            return f"Error formatting performance analysis: {str(e)}"
    
    def _format_uptime_response(self, data: Dict[str, Any], url: str) -> str:
        """Format uptime monitoring response"""
        try:
            content = data.get("content", [])
            if content and len(content) > 0:
                text = content[0].get("text", "")
                if text:
                    uptime_data = json.loads(text)
                    
                    response = f"🔍 **Uptime Analysis for {url}**\n\n"
                    
                    if 'monitor_id' in uptime_data:
                        response += f"**Monitor ID:** {uptime_data['monitor_id']}\n"
                        response += f"**Status:** {uptime_data.get('status', 'Unknown')}\n"
                        response += f"**Uptime:** {uptime_data.get('uptime', 'Unknown')}%\n"
                        response += f"**Response Time:** {uptime_data.get('response_time', 'Unknown')}ms\n"
                    elif 'message' in uptime_data:
                        response += f"**Status:** {uptime_data['message']}\n"
                    
                    response += f"\n⏰ Check completed at: {uptime_data.get('timestamp', 'Unknown')}"
                    return response
            
            return "Uptime data received but couldn't parse the results."
        except Exception as e:
            logger.error(f"Error formatting uptime response: {str(e)}")
            return f"Error formatting uptime analysis: {str(e)}"
    
    def _format_monitor_response(self, data: Dict[str, Any], url: str) -> str:
        """Format monitor creation response"""
        try:
            content = data.get("content", [])
            if content and len(content) > 0:
                text = content[0].get("text", "")
                if text:
                    monitor_data = json.loads(text)
                    
                    response = f"✅ **Monitor Creation for {url}**\n\n"
                    
                    if monitor_data.get('success'):
                        response += f"**Status:** Monitor created successfully!\n"
                        response += f"**Monitor ID:** {monitor_data.get('monitor_id', 'Unknown')}\n"
                        response += f"**Friendly Name:** {monitor_data.get('friendly_name', url)}\n"
                        response += f"**Check Interval:** Every {monitor_data.get('interval', 300)} seconds\n"
                    else:
                        response += f"**Status:** {monitor_data.get('message', 'Failed to create monitor')}\n"
                    
                    response += f"\n⏰ Created at: {monitor_data.get('timestamp', 'Unknown')}"
                    return response
            
            return "Monitor creation data received but couldn't parse the results."
        except Exception as e:
            logger.error(f"Error formatting monitor response: {str(e)}")
            return f"Error formatting monitor creation: {str(e)}"
    
    def _get_default_response(self, message: str) -> str:
        """Get default response for unrecognized messages"""
        return """I can help you with website performance analysis, uptime monitoring, and creating monitors. 

Try asking me to:
• "Analyze performance for [website]" - Check website speed and performance metrics
• "Check uptime for [website]" - See if a website is online and responsive  
• "Create monitor for [website]" - Set up ongoing monitoring for a website

For example: "Analyze performance for nike.com" or "Check uptime for google.com" """

# Global agent instance
marketing_agent = SimpleMarketingAgent()

@app.get("/")
async def root():
    """Root endpoint - provides API information"""
    return {
        "message": "Marketing Agent Backend API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "tools": "/tools", 
            "health": "/health",
            "status": "/status",
            "docs": "/docs"
        },
        "description": "Backend API for marketing analytics with Google PageSpeed and UptimeRobot integration"
    }

@app.get("/favicon.ico")
async def favicon():
    """Favicon endpoint - returns 204 to prevent 404 errors"""
    return "", 204

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check MCP server availability
    mcp_available = await marketing_agent.mcp_client.is_server_available()
    
    status = {
        "status": "healthy",
        "mcp_server": "available" if mcp_available else "unavailable",
        "timestamp": str(asyncio.get_event_loop().time())
    }
    
    if not mcp_available:
        status["warning"] = "MCP server is not running. Start it with: cd mcp-server && npm run simple-http"
    
    return status

@app.get("/status")
async def detailed_status():
    """Detailed status endpoint"""
    try:
        # Check MCP server
        mcp_available = await marketing_agent.mcp_client.is_server_available()
        mcp_tools = await marketing_agent.mcp_client.list_tools() if mcp_available else []
        
        return {
            "backend": {
                "status": "running",
                "version": "1.0.0",
                "uptime": "healthy"
            },
            "mcp_server": {
                "status": "available" if mcp_available else "unavailable",
                "url": "http://localhost:3001",
                "tools_count": len(mcp_tools),
                "tools": mcp_tools
            },
            "endpoints": {
                "chat": "/chat",
                "tools": "/tools",
                "health": "/health",
                "status": "/status",
                "docs": "/docs"
            },
            "capabilities": {
                "performance_analysis": True,
                "uptime_monitoring": True,
                "monitor_creation": True,
                "logging": True
            }
        }
    except Exception as e:
        return {
            "backend": {"status": "error"},
            "error": str(e)
        }

@app.get("/docs")
async def api_docs():
    """API documentation endpoint"""
    return {
        "title": "Marketing Agent Backend API",
        "version": "1.0.0",
        "description": "Backend API for marketing analytics with Google PageSpeed and UptimeRobot integration",
        "endpoints": {
            "GET /": {
                "description": "API information and endpoints",
                "response": "JSON with API details"
            },
            "GET /health": {
                "description": "Health check with MCP server status",
                "response": "JSON with health status"
            },
            "GET /status": {
                "description": "Detailed service status",
                "response": "JSON with all service information"
            },
            "GET /tools": {
                "description": "List available MCP tools",
                "response": "JSON with tool definitions"
            },
            "POST /chat": {
                "description": "Process user messages and return responses",
                "request_body": {
                    "messages": "array of message objects",
                    "session_id": "optional session identifier"
                },
                "response": "JSON with assistant response"
            }
        },
        "usage_examples": {
            "performance_analysis": {
                "method": "POST",
                "url": "/chat",
                "body": {
                    "messages": [{"content": "analyze nike.com"}]
                }
            },
            "uptime_check": {
                "method": "POST", 
                "url": "/chat",
                "body": {
                    "messages": [{"content": "check uptime for google.com"}]
                }
            },
            "monitor_creation": {
                "method": "POST",
                "url": "/chat", 
                "body": {
                    "messages": [{"content": "create monitor for facebook.com"}]
                }
            }
        }
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat endpoint"""
    logger.info("Chat endpoint called")
    try:
        user_message = request.messages[-1]["content"] if request.messages else ""
        logger.info(f"User message received: '{user_message}'")
        
        response = await marketing_agent.process_message(user_message)
        
        # Ensure response is not None
        if response is None:
            response = "I apologize, but I encountered an issue processing your request. Please try again."
            logger.warning("Response was None, using fallback message")
        
        logger.info("Response generated successfully")
        return ChatResponse(response=response)
    except Exception as e:
        error_msg = f"Chat endpoint error: {str(e)}"
        logger.error(f"Chat endpoint error: {error_msg}")
        # Return a proper error response
        return ChatResponse(response="I apologize, but I encountered an error. Please check the logs for details.")

@app.get("/tools")
async def list_available_tools():
    """List available marketing tools"""
    try:
        tools = await marketing_agent.mcp_client.list_tools()
        return {"tools": tools}
    except Exception as e:
        logger.error(f"Tools endpoint error: {str(e)}")
        return {"tools": [], "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
