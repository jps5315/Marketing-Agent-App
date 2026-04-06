import asyncio
import subprocess
import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import httpx
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

app = FastAPI(title="Marketing Agent Backend")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    session_id: Optional[str] = None

class WeatherTool(BaseModel):
    name: str
    description: str
    parameters: dict

class MCPClient:
    def __init__(self):
        self.process = None
        self.mcp_server_host = os.getenv("MCP_SERVER_HOST", "localhost")
        self.mcp_server_port = os.getenv("MCP_SERVER_PORT", "3001")
        
    async def start_mcp_server(self):
        """Start the MCP server as a subprocess"""
        try:
            # Start MCP server
            mcp_server_path = os.path.join(os.path.dirname(__file__), "..", "mcp-server")
            self.process = await asyncio.create_subprocess_exec(
                "node", "index.js",
                cwd=mcp_server_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait a moment for server to start
            await asyncio.sleep(2)
            
            # Initialize MCP connection
            await self.initialize_mcp()
            
        except Exception as e:
            print(f"Failed to start MCP server: {e}")
            raise
    
    async def initialize_mcp(self):
        """Initialize MCP connection and list available tools"""
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "weather-agent-backend",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await self.send_mcp_request(initialize_request)
        return response
    
    async def send_mcp_request(self, request):
        """Send a request to MCP server"""
        if not self.process:
            raise Exception("MCP server not running")
            
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        return json.loads(response_line.decode())
    
    async def list_tools(self):
        """List available MCP tools"""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = await self.send_mcp_request(request)
        return response.get("result", {}).get("tools", [])
    
    async def call_tool(self, tool_name: str, arguments: dict):
        """Call an MCP tool"""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        response = await self.send_mcp_request(request)
        return response.get("result", {})
    
    async def stop(self):
        """Stop the MCP server"""
        if self.process:
            self.process.terminate()
            await self.process.wait()

class MarketingAgent:
    def __init__(self):
        self.mcp_client = MCPClient()
        self.llm = ChatGroq(
            model="llama3-70b-8192",
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.tools = []
        self.agent_executor = None
        
    async def initialize(self):
        """Initialize the agent with MCP tools"""
        await self.mcp_client.start_mcp_server()
        
        # Get available tools from MCP
        mcp_tools = await self.mcp_client.list_tools()
        
        # Convert MCP tools to LangChain tools
        self.tools = []
        for tool in mcp_tools:
            langchain_tool = Tool(
                name=tool["name"],
                description=tool["description"],
                func=lambda args, tool_name=tool["name"]: self.call_mcp_tool(tool_name, args)
            )
            self.tools.append(langchain_tool)
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional marketing and web performance analyst. You have access to real-time website performance data, uptime monitoring, and can create website monitors through UptimeRobot and Google PageSpeed Insights.
            
            Use the available tools to provide actionable marketing insights and recommendations. Always be specific about data and provide
            practical advice based on the website analytics and performance metrics.
            
            Available tools:
            - get_website_performance: Get performance metrics and optimization suggestions
            - get_website_uptime: Get website uptime and monitoring status
            - create_monitor: Create a new website monitor in UptimeRobot
            - get_all_monitors: Get all monitors from UptimeRobot account
            
            When users ask about website performance, uptime, monitoring, or marketing optimization, always try to get the most relevant information for their needs.
            Provide strategic recommendations based on the data."""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    async def call_mcp_tool(self, tool_name: str, arguments: dict):
        """Call an MCP tool and return the result"""
        try:
            result = await self.mcp_client.call_tool(tool_name, arguments)
            
            # Extract the text content from the result
            if "content" in result and len(result["content"]) > 0:
                content = result["content"][0]
                if content.get("type") == "text":
                    return content.get("text", "No data returned")
            
            return str(result)
            
        except Exception as e:
            return f"Error calling {tool_name}: {str(e)}"
    
    async def process_message(self, message: str) -> str:
        """Process a user message and return the agent's response"""
        if not self.agent_executor:
            await self.initialize()
        
        try:
            response = await self.agent_executor.ainvoke({"input": message})
            return response.get("output", "I apologize, but I couldn't process your request.")
        except Exception as e:
            return f"I apologize, but an error occurred: {str(e)}"
    
    async def cleanup(self):
        """Clean up resources"""
        await self.mcp_client.stop()

# Global agent instance
marketing_agent = MarketingAgent()

@app.on_event("startup")
async def startup_event():
    """Initialize the marketing agent on startup"""
    await marketing_agent.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    await marketing_agent.cleanup()

@app.post("/chat")
async def chat(request: ChatRequest):
    """Process a chat message and return the agent's response"""
    try:
        # Get the last user message
        user_message = ""
        for message in reversed(request.messages):
            if message.role == "user":
                user_message = message.content
                break
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found")
        
        # Process the message
        response = await marketing_agent.process_message(user_message)
        
        return {
            "response": response,
            "session_id": request.session_id or "default"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/tools")
async def list_available_tools():
    """List available marketing tools"""
    try:
        mcp_tools = await marketing_agent.mcp_client.list_tools()
        return {"tools": mcp_tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
