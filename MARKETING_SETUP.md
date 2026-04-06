# Marketing Agent Application - Setup Guide

## Overview

This is a full-stack marketing analytics application that demonstrates real-world value for marketers. The application provides AI-powered insights using SimilarWeb data and free LLM capabilities.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (version 18 or higher)
- **Python** (version 3.9 or higher)
- **npm** or **yarn** (for Node.js package management)
- **pip** (for Python package management)

## Step 1: Get API Keys

### SimilarWeb API Key (Required)
1. Visit [SimilarWeb Developers](https://developers.similarweb.com/)
2. Sign up for an account
3. Navigate to your dashboard
4. Generate an API key
5. Choose a plan (free tier available for development)
6. Copy the key for later use

### Groq API Key (Required for Free LLM)
1. Visit [Groq Console](https://console.groq.com/)
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key for later use
6. **Free tier includes**: 1,000 requests/day, 6,000 tokens/minute

## Step 2: Project Setup

### Navigate to Project
```bash
cd weather-agent-app
```

### Setup MCP Server
```bash
cd mcp-server

# Install dependencies
npm install

# Create environment file
copy .env.example .env  # On Windows
# or
cp .env.example .env   # On Mac/Linux

# Edit .env file and add your SimilarWeb API key
# SIMILARWEB_API_KEY=your_actual_similarweb_key_here
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
# GROQ_API_KEY=your_actual_groq_key_here
# SIMILARWEB_API_KEY=your_actual_similarweb_key_here
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
cd weather-agent-app/mcp-server
npm run dev
```
You should see: `Marketing MCP Server connected and ready!`

### Terminal 2: Start Agent Backend
```bash
cd weather-agent-app/agent-backend
python app.py
```
You should see the FastAPI server starting on port 8000

### Terminal 3: Start Frontend
```bash
cd weather-agent-app/frontend
npm run dev
```
The frontend will be available at http://localhost:3000

## Step 4: Verify the Setup

1. Open your web browser
2. Navigate to http://localhost:3000
3. You should see the Marketing Agent interface
4. Try asking: "Analyze the traffic for nike.com"

## Marketing Use Cases

### Traffic Analysis
- "Show me traffic metrics for amazon.com"
- "What's the bounce rate for facebook.com?"
- "How many visitors does tesla.com get?"

### Competitor Analysis
- "Compare nike.com vs adidas.com"
- "Who are the main competitors of apple.com?"
- "Market position of microsoft.com"

### Audience Insights
- "What's the audience demographics for linkedin.com?"
- "Age distribution of instagram.com users"
- "Interests of reddit.com visitors"

### Marketing Strategy
- "Marketing insights for startup.com"
- "How to improve traffic for mywebsite.com"
- "Recommendations based on competitor analysis"

## Troubleshooting

### Common Issues

**1. MCP Server not starting**
- Ensure Node.js is installed correctly
- Check that your SimilarWeb API key is valid
- Verify the .env file exists in the mcp-server directory

**2. Agent Backend failing**
- Ensure Python 3.9+ is installed
- Check that all requirements are installed: `pip install -r requirements.txt`
- Verify your Groq API key is valid
- Make sure the MCP Server is running first

**3. Frontend not connecting**
- Ensure both MCP Server and Agent Backend are running
- Check that ports 3001 and 8000 are available
- Verify no firewall is blocking the connections

**4. API Key Errors**
- SimilarWeb: May require account activation
- Groq: Free tier has rate limits (1,000 requests/day)
- Check for typos in API key copying

**5. Data Not Available**
- SimilarWeb may not have data for all websites
- Try popular websites first (amazon.com, google.com, facebook.com)
- Some domains require premium SimilarWeb plans

## Performance Tips

### API Rate Limits
- **Groq**: 1,000 requests/day, 6,000 tokens/minute
- **SimilarWeb**: Varies by plan
- Implement caching for frequently requested data

### Optimization
- Use specific domain names
- Request multiple metrics in single calls
- Cache results for popular websites

## Development Features

### Available Tools
1. **get_website_traffic**: Traffic and engagement metrics
2. **get_traffic_sources**: Traffic sources breakdown
3. **get_competitor_analysis**: Competitor insights
4. **get_demographics**: Audience demographics

### AI Capabilities
- Natural language understanding
- Multi-tool coordination
- Strategic recommendations
- Data interpretation

## Production Considerations

For production deployment:

1. **Security**: Add authentication and rate limiting
2. **Scaling**: Consider Redis for caching
3. **Monitoring**: Add logging and metrics
4. **Cost Management**: Monitor API usage
5. **Error Handling**: Graceful degradation

## Sample Marketing Queries

```text
"Analyze the marketing strategy for nike.com"
"Compare facebook.com vs twitter.com traffic"
"What's the audience profile for pinterest.com?"
"Show me traffic sources for youtube.com"
"Marketing insights for e-commerce websites"
"Competitor analysis in the tech industry"
```

## Support

If you encounter issues:

1. Check API key validity
2. Verify service startup order
3. Review rate limits
4. Check network connectivity
5. Review error logs in each terminal

## Architecture Benefits

- **Real-time Data**: Live marketing analytics
- **AI Insights**: Intelligent recommendations
- **Scalable**: Microservices architecture
- **Cost-effective**: Free LLM with Groq
- **Professional**: Enterprise-ready features
