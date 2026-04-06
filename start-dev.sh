#!/bin/bash

# Development Startup Script for Weather Agent App
# This script starts all three services in separate terminal windows

echo "Starting Weather Agent Application Development Environment..."

# Check if we're in the right directory
if [ ! -f "mcp-server/package.json" ]; then
    echo "Error: Please run this script from the weather-agent-app root directory"
    exit 1
fi

# Function to open a new terminal window and run a command
open_terminal() {
    local title=$1
    local command=$2
    local dir=$3
    
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal --title="$title" -- bash -c "cd $dir; $command; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -title "$title" -e "cd $dir; $command; bash"
    elif command -v osascript &> /dev/null; then
        # macOS
        osascript -e "tell application \"Terminal\" to do script \"cd $dir && $command\""
    else
        echo "Could not find a suitable terminal emulator"
        echo "Please manually run the following commands in separate terminals:"
        echo "1. cd mcp-server && npm run dev"
        echo "2. cd agent-backend && python app.py"
        echo "3. cd frontend && npm run dev"
        exit 1
    fi
}

# Start MCP Server
echo "Starting MCP Server..."
open_terminal "MCP Server" "npm run dev" "mcp-server"
sleep 3

# Start Agent Backend
echo "Starting Agent Backend..."
open_terminal "Agent Backend" "python app.py" "agent-backend"
sleep 3

# Start Frontend
echo "Starting Frontend..."
open_terminal "Frontend" "npm run dev" "frontend"

echo "All services started!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "MCP Server: Running on port 3001"
echo ""
echo "Opening the application in your browser..."

# Try to open the browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
elif command -v open &> /dev/null; then
    open http://localhost:3000
elif command -v start &> /dev/null; then
    start http://localhost:3000
fi
