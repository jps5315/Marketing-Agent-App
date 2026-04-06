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

# Load environment variables
load_dotenv()

# Pydantic models
class ChatRequest(BaseModel):
    messages: list
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str

class MCPClient:
    def __init__(self):
        self.base_url = f"http://{os.getenv('MCP_SERVER_HOST', 'localhost')}:{os.getenv('MCP_SERVER_PORT', '3001')}"
        self.timeout = httpx.Timeout(6000.0)  # 100 minutes for all operations
        logger.info(f"MCP Client initialized with base URL: {self.base_url}")
    
    async def is_server_available(self) -> bool:
        """Check if MCP server is available"""
        logger.info(f"Checking MCP server availability at: {self.base_url}/health")
        try:
            async with httpx.AsyncClient(timeout=6000.0) as client:  # 100 minutes for health checks
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
    """Gemini API client for LLM support"""
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.timeout = httpx.Timeout(6000.0)  # 100 minutes for LLM operations
        logger.info(f"Gemini Client initialized with API key: {'✓' if self.api_key else '✗'}")
    
    async def query(self, prompt: str, context: str = "") -> str:
        """Query Gemini API with context"""
        if not self.api_key:
            logger.warning("GOOGLE_GEMINI_API_KEY not found - LLM queries will fail")
            return "I apologize, but LLM service is not available. Please set GOOGLE_GEMINI_API_KEY environment variable."
        
        try:
            system_prompt = """You are a helpful marketing analytics assistant. You have access to web performance and monitoring tools.
            When users ask questions that require analysis beyond simple tool calls, provide helpful insights and recommendations.
            Keep responses concise and actionable."""
            
            full_prompt = f"Context: {context}\n\nUser Question: {prompt}"
            
            logger.info(f"Querying Gemini LLM with prompt: {prompt[:100]}...")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/models/gemini-2.5-flash:generateContent",
                    json={
                        "contents": [{
                            "parts": [{
                                "text": f"{system_prompt}\n\n{full_prompt}"
                            }]
                        }]
                    },
                    headers={
                        "Content-Type": "application/json",
                        "X-goog-api-key": self.api_key
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = data["candidates"][0]["content"]["parts"][0]["text"]
                    logger.info(f"Gemini LLM response received: {result[:100]}...")
                    return result
                else:
                    error_msg = f"Gemini API error: {response.status_code} - {response.text}"
                    logger.error(f"Gemini LLM Error: {error_msg}")
                    return f"I apologize, but I encountered an error with the LLM service: {error_msg}"
                    
        except Exception as e:
            error_msg = f"Gemini LLM exception: {str(e)}"
            logger.error(f"Gemini LLM Exception: {error_msg}")
            return f"I apologize, but I encountered an error with the LLM service: {error_msg}"
    
    async def list_models(self) -> list:
        """List available Gemini models"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"X-goog-api-key": self.api_key}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    for model in data.get("models", []):
                        if "generateContent" in model.get("supportedGenerationMethods", []):
                            models.append({
                                "name": model.get("name"),
                                "displayName": model.get("displayName"),
                                "description": model.get("description")
                            })
                    return models
                else:
                    logger.error(f"Failed to list models: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Exception listing models: {str(e)}")
            return []

class SimpleMarketingAgent:
    def __init__(self):
        self.mcp_client = MCPClient()
        self.grok_client = GrokClient()
        self.session_context = {}  # Store analysis results per session
        
    async def process_message(self, user_message: str, session_id: str = "default") -> str:
        """Process user message with enhanced logic including LLM support"""
        logger.info(f"🔍 Starting message analysis: '{user_message}'")
        logger.info(f"📝 Message length: {len(user_message)} characters")
        
        message_lower = user_message.lower()
        
        # Check for URLs in the message
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, user_message)
        logger.info(f"🔗 URLs found: {urls}")
        
        # Define tool-related keywords
        performance_keywords = ['performance', 'speed', 'analyze', 'check', 'test', 'audit']
        uptime_keywords = ['uptime', 'monitor', 'status', 'available', 'down', 'check']
        monitor_keywords = ['create monitor', 'add monitor', 'new monitor', 'setup monitor']
        complex_keywords = ['why', 'how', 'what', 'explain', 'recommend', 'suggest', 'improve', 'optimize', 'strategy', 'best practices']
        
        logger.info(f"🔧 Available keywords - Performance: {performance_keywords}")
        logger.info(f"🔧 Available keywords - Uptime: {uptime_keywords}")
        logger.info(f"🔧 Available keywords - Monitor: {monitor_keywords}")
        logger.info(f"🔧 Available keywords - LLM: {complex_keywords}")
        
        # Simple tool-based queries
        if urls:
            url = urls[0]
            logger.info(f"URL detected: {url}")
            
            # Performance analysis
            if any(keyword in message_lower for keyword in performance_keywords):
                logger.info(f"Performance keywords matched: {[k for k in performance_keywords if k in message_lower]}")
                logger.info("🎯 Tool Selected: get_website_performance")
                logger.info("Performance analysis requested")
                result = await self.mcp_client.call_tool("get_website_performance", {"url": url})
                if "error" not in result:
                    data = json.loads(result["content"][0]["text"])
                    return f"📊 **Performance Analysis for {url}**\n\n**Performance Score: {data.get('performance_score', 0)}/100**\n\n**Key Metrics:**\n- First Contentful Paint: {data.get('metrics', {}).get('first_contentful_paint', 0):.0f}ms\n- Largest Contentful Paint: {data.get('metrics', {}).get('largest_contentful_paint', 0):.0f}ms\n- Cumulative Layout Shift: {data.get('metrics', {}).get('cumulative_layout_shift', 0):.3f}\n- Total Blocking Time: {data.get('metrics', {}).get('total_blocking_time', 0):.0f}ms\n\n**Top Opportunities:**\n" + "\n".join([f"• {opp.get('title', 'Unknown')}" for opp in data.get('opportunities', [])[:3]])
                else:
                    return f"I apologize, but I encountered an error analyzing the performance of {url}: {result.get('error', 'Unknown error')}"
            
            # Uptime check
            elif any(keyword in message_lower for keyword in uptime_keywords):
                logger.info(f"Uptime keywords matched: {[k for k in uptime_keywords if k in message_lower]}")
                logger.info("🎯 Tool Selected: get_website_uptime")
                logger.info("Uptime check requested")
                result = await self.mcp_client.call_tool("get_website_uptime", {"url": url, "friendly_name": url})
                if "error" not in result:
                    data = json.loads(result["content"][0]["text"])
                    return f"🔍 **Uptime Check for {url}**\n\n{data}"
                else:
                    return f"I apologize, but I encountered an error checking uptime for {url}: {result.get('error', 'Unknown error')}"
            
            # Create monitor
            elif any(keyword in message_lower for keyword in monitor_keywords):
                logger.info(f"Monitor keywords matched: {[k for k in monitor_keywords if k in message_lower]}")
                logger.info("🎯 Tool Selected: create_monitor")
                logger.info("Monitor creation requested")
                result = await self.mcp_client.call_tool("create_monitor", {"url": url, "friendly_name": url})
                if "error" not in result:
                    data = json.loads(result["content"][0]["text"])
                    return f"📈 **Monitor Created for {url}**\n\n{data}"
                else:
                    return f"I apologize, but I encountered an error creating a monitor for {url}: {result.get('error', 'Unknown error')}"
        
        # Complex queries that need LLM analysis
        if any(keyword in message_lower for keyword in complex_keywords):
            logger.info(f"Complex keywords matched: {[k for k in complex_keywords if k in message_lower]}")
            logger.info("🤖 Tool Selected: Gemini LLM")
            logger.info("Complex query detected, using LLM")
            
            # Get context from available tools and session history
            context = ""
            context_sources = []
            
            # Add previous analysis results from session
            if session_id in self.session_context:
                context += f"Previous Analysis Results:\n{self.session_context[session_id]}\n\n"
                context_sources.append("Session History")
                logger.info(f"📚 Found session context for session: {session_id}")
                logger.info(f"📝 Session context length: {len(self.session_context[session_id])} characters")
            else:
                logger.info(f"📝 No previous session context found for session: {session_id}")
            
            # Add current URLs found
            if urls:
                context += f"Current Website URL: {urls[0]}\n"
                context_sources.append("Current URL")
                logger.info(f"🔗 Using current URL for context: {urls[0]}")
                
                # Try to get fresh performance data for context
                try:
                    perf_result = await self.mcp_client.call_tool("get_website_performance", {"url": urls[0]})
                    if "error" not in perf_result:
                        perf_data = json.loads(perf_result["content"][0]["text"])
                        context += f"Current Performance Data:\n"
                        context += f"- Performance Score: {perf_data.get('performance_score', 0)}/100\n"
                        context += f"- First Contentful Paint: {perf_data.get('metrics', {}).get('first_contentful_paint', 0):.0f}ms\n"
                        context += f"- Largest Contentful Paint: {perf_data.get('metrics', {}).get('largest_contentful_paint', 0):.0f}ms\n"
                        context += f"- Cumulative Layout Shift: {perf_data.get('metrics', {}).get('cumulative_layout_shift', 0):.3f}\n"
                        context += f"- Total Blocking Time: {perf_data.get('metrics', {}).get('total_blocking_time', 0):.0f}ms\n"
                        
                        # Add top opportunities
                        opportunities = perf_data.get('opportunities', [])[:3]
                        if opportunities:
                            context += "Top Performance Opportunities:\n"
                            for i, opp in enumerate(opportunities, 1):
                                context += f"{i}. {opp.get('title', 'Unknown')}\n"
                        
                        context_sources.append("Fresh Performance Data")
                        logger.info(f"📊 Fresh performance data retrieved for context")
                        logger.info(f"📈 Performance Score: {perf_data.get('performance_score', 0)}/100")
                        logger.info(f"🎯 Opportunities found: {len(opportunities)}")
                        
                        # Store in session context
                        self.session_context[session_id] = context
                        logger.info(f"💾 Context stored in session: {session_id}")
                    else:
                        logger.warning(f"⚠️ Performance data retrieval failed: {perf_result.get('error', 'Unknown error')}")
                except Exception as e:
                    logger.error(f"❌ Exception getting performance data: {str(e)}")
            else:
                logger.info("🔗 No URLs found in current message")
            
            # Log context summary
            logger.info(f"🔧 Context sources used: {context_sources}")
            logger.info(f"📏 Total context length: {len(context)} characters")
            logger.info(f"📋 Context preview:\n{context[:300]}...")
            
            # Query LLM with enhanced context
            logger.info("🤖 Sending query to Gemini LLM with context...")
            llm_response = await self.grok_client.query(user_message, context)
            logger.info(f"🧠 LLM response received: {len(llm_response)} characters")
            logger.info(f"📝 LLM response preview:\n{llm_response[:200]}...")
            
            # Store LLM response in session context
            self.session_context[session_id] = f"LLM Analysis: {llm_response}"
            logger.info(f"💾 LLM response stored in session: {session_id}")
            
            return f"🤖 **AI Analysis with Context**\n\n{llm_response}"
        
        # Default response
        logger.info("❌ No tool matched - returning default help response")
        logger.info("Available tools: get_website_performance, get_website_uptime, create_monitor, Gemini LLM")
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

# FastAPI app
app = FastAPI(title="Marketing Agent Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Marketing Agent Backend", "version": "1.0.0"}

@app.get("/favicon.ico")
async def favicon():
    """Favicon endpoint to avoid 404"""
    return {"message": "Favicon not available"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check MCP server availability
        mcp_available = await marketing_agent.mcp_client.is_server_available()
        
        status = {
            "status": "healthy",
            "service": "marketing-agent-backend",
            "version": "1.0.0",
            "mcp_server": "available" if mcp_available else "unavailable"
        }
        
        logger.info(f"Health check completed - MCP Server: {status['mcp_server']}")
        return status
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}

@app.get("/status")
async def detailed_status():
    """Detailed status endpoint"""
    try:
        # Get MCP server status
        mcp_available = await marketing_agent.mcp_client.is_server_available()
        
        # Get available tools
        tools = []
        if mcp_available:
            tools = await marketing_agent.mcp_client.list_tools()
        
        status = {
            "backend": {
                "status": "running",
                "version": "1.0.0",
                "service": "marketing-agent-backend"
            },
            "mcp_server": {
                "status": "available" if mcp_available else "unavailable",
                "url": marketing_agent.mcp_client.base_url,
                "tools_count": len(tools),
                "tools": tools
            }
        }
        
        logger.info(f"Status check completed - MCP Server: {status['mcp_server']['status']}")
        return status
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return {"status": "error", "error": str(e)}

@app.get("/tools")
async def list_tools_endpoint():
    """List available tools endpoint"""
    try:
        tools = await marketing_agent.mcp_client.list_tools()
        return {"tools": tools}
    except Exception as e:
        logger.error(f"List tools error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_gemini_models():
    """List available Gemini models endpoint"""
    try:
        models = await marketing_agent.grok_client.list_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"List models error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/docs")
async def api_docs():
    """API documentation endpoint"""
    return {
        "title": "Marketing Agent Backend API",
        "version": "1.0.0",
        "description": "Backend service for marketing analytics with MCP integration",
        "endpoints": {
            "/": "Root endpoint",
            "/health": "Health check",
            "/status": "Detailed status with MCP server info",
            "/tools": "List available MCP tools",
            "/models": "List available Gemini models",
            "/chat": "Chat endpoint for processing user messages",
            "/docs": "This API documentation"
        },
        "usage": {
            "chat": {
                "method": "POST",
                "endpoint": "/chat",
                "body": {
                    "messages": [{"content": "Analyze performance of nike.com"}],
                    "session_id": "default"
                },
                "example": "curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{\"messages\":[{\"content\":\"Analyze performance of nike.com\"}],\"session_id\":\"default\"}'"
            }
        }
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat endpoint for processing user messages"""
    logger.info("Chat endpoint called")
    logger.info(f"Session ID: {request.session_id}")
    try:
        user_message = request.messages[-1]["content"] if request.messages else ""
        response = await marketing_agent.process_message(user_message, request.session_id)
        if response is None:
            response = "I apologize, but I encountered an issue processing your request."
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return ChatResponse(response="I apologize, but I encountered an error.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
