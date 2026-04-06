# Development Startup Script for Marketing Agent App
# This script starts all three services in separate windows

Write-Host "Starting Marketing Agent Application Development Environment..." -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "mcp-server\package.json")) {
    Write-Host "Error: Please run this script from the marketing-agent-app root directory" -ForegroundColor Red
    exit 1
}

# Start MCP Server
Write-Host "Starting Marketing MCP Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd mcp-server; npm run dev" -WindowStyle Normal
Start-Sleep -Seconds 3

# Start Agent Backend
Write-Host "Starting Marketing Agent Backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd agent-backend; python simple_app.py" -WindowStyle Normal
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "Starting Marketing Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -WindowStyle Normal

Write-Host "All services started!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "MCP Server: Running on port 3001" -ForegroundColor Cyan
Write-Host ""
Write-Host "Marketing Agent ready for analytics!" -ForegroundColor Magenta
Write-Host "Try: 'Analyze traffic for nike.com'" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to open the application in your browser..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Start-Process "http://localhost:3000"
