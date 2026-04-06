# Marketing Agent Application - Setup Guide

## Overview

This is a full-stack agent-driven Marketing application that demonstrates end-to-end development with modern technologies. The application consists of three main components:

1. **MCP Server** - A wrapper service for GooglePagespeed API
2. **Agent Backend** - LLM-powered backend using customized orchestration
3. **Frontend** - Modern React web application

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (version 18 or higher)
- **Python** (version 3.9 or higher)
- **npm** or **yarn** (for Node.js package management)
- **pip** (for Python package management)

## Step 1: Get API Keys

### Googlepagespeed API Key (Required)
1. Visit GooglePageSpeed
2. Sign up for a free account
3. Navigate to your account dashboard
4. Generate an API key
5. Copy the key for later use

### Gemini API Key (Required for LLM)
1. Visit Google AI Studio
2. Sign up or log in
3. Navigate to the API Keys section
4. Create a new API key
5. Copy the key for later use

## Step 2: Project Setup

### Clone and Navigate
```bash
# Navigate to the project directory
cd Marketing-Agent-App
```

### Setup MCP Server
```bash
cd mcp-server

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Edit .env file and add your OpenWeatherMap API key
# GooglePagespeed_API_KEY=your_actual_api_key_here
```

### Setup Agent Backend
```bash
cd ../agent-backend

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env  # On Windows
# or
cp .env.example .env   # On Mac/Linux

# Edit .env file and add your API keys
# Gemini_API_KEY=your_actual_openai_key_here
# MCP_SERVER_HOST=localhost
# MCP_SERVER_PORT=3001
# BACKEND_HOST=localhost
# BACKEND_PORT=8000
```

### Setup Frontend
```bash
cd ../frontend

# Install dependencies
npm install
```

## Step 3: Running the Application

The application requires all three services to be running simultaneously. Open **three separate terminal windows**:

### Terminal 1: Start MCP Server
```bash
cd Marketing-Agent-App/mcp-server
npm run dev
```
You should see: `MCP Server connected and ready!`

### Terminal 2: Start Agent Backend
```bash
cd Marketing-Agent-App/agent-backend
python app.py
```
You should see the FastAPI server starting on port 8000

### Terminal 3: Start Frontend
```bash
cd Marketing-Agent-App/frontend
npm run dev
```
The frontend will be available at http://localhost:3000

## Step 4: Verify the Setup

1. Open your web browser
2. Navigate to http://localhost:3000
3. You should see the Weather Agent interface
4. Try asking: "Analyze the performance of https://www.nike.com?"

## Troubleshooting

### Common Issues

**1. MCP Server not starting**
- Ensure Node.js is installed correctly
- Check that your OpenWeatherMap API key is valid
- Verify the .env file exists in the mcp-server directory

**2. Agent Backend failing**
- Ensure Python 3.9+ is installed
- Check that all requirements are installed: `pip install -r requirements.txt`
- Verify your OpenAI API key is valid and has credits
- Make sure the MCP Server is running first

**3. Frontend not connecting**
- Ensure both MCP Server and Agent Backend are running
- Check that ports 3001 and 8000 are available
- Verify no firewall is blocking the connections

**4. API Key Errors**
- Double-check your API keys are correctly copied
- Ensure there are no extra spaces or characters
- Verify your OpenWeatherMap key is activated (can take a few minutes)

**5. Port Conflicts**
- If ports are in use, you can change them in the .env files
- Ensure all three services use different ports

### Testing Individual Components

**Test MCP Server:**
```bash
cd mcp-server
node -e "
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
// Test basic server functionality
console.log('MCP Server dependencies loaded successfully');
"
```

**Test Agent Backend:**
```bash
cd agent-backend
python -c "
import langchain
import fastapi
print('All dependencies imported successfully')
"
```

**Test Frontend:**
```bash
cd frontend
npm run build
# Should complete without errors
```

## Development Tips

### Monitoring Logs
- MCP Server: Check the terminal running the MCP server
- Agent Backend: FastAPI provides detailed logs
- Frontend: Browser console shows network requests and errors

### Making Changes
- MCP Server: Restart with `npm run dev` (auto-reloads)
- Agent Backend: Restart with `python app.py`
- Frontend: Next.js hot-reloads automatically

### Environment Variables
Always keep your API keys secure:
- Never commit .env files to version control
- Use different keys for development and production
- Regularly rotate your API keys

## Production Deployment

For production deployment, consider:

1. **Environment Variables**: Use proper environment management
2. **HTTPS**: Enable SSL/TLS for all services
3. **Security**: Implement authentication and rate limiting
4. **Scaling**: Consider containerization with Docker
5. **Monitoring**: Add logging and monitoring solutions

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all services are running in the correct order
3. Ensure API keys are valid and have sufficient credits
4. Check that all dependencies are installed correctly

## Architecture Overview

```
User (Browser) → Frontend (Next.js) → Agent Backend (FastAPI + Custome orchestration) → MCP Server → GooglePagespeed API
```

- **Frontend**: React-based UI for user interaction
- **Agent Backend**: Processes natural language, makes decisions using LLM
- **MCP Server**: Standardized interface to weather data
- **OpenWeatherMap**: Source of weather information
