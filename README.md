# Marketing Agent Application - Free APIs

A full-stack agent-driven application that demonstrates end-to-end development with **100% FREE APIs**:
- Google PageSpeed Insights API for performance analysis
- UptimeRobot API for website monitoring  
- Gemini API for free LLM capabilities
- Modern React frontend for marketing insights

## 🎯 Why This Matters

**Professional marketing analytics without paid subscriptions!** This application provides enterprise-level features using only free APIs, saving you $160-750 per month compared to paid alternatives.

## Project Structure

```
weather-agent-app/
├── mcp-server/          # MCP Server wrapper for free APIs
├── agent-backend/       # LLM Agent backend with Groq
├── frontend/            # React web application
└── FREE_API_SETUP.md    # Detailed free API setup guide
```

## ✨ Features (All Free!)

- **Website Performance Analysis** - Google PageSpeed Insights
- **Uptime Monitoring** - Real-time website availability tracking
- **AI-Powered Recommendations** - Llama 3.1 via Groq
- **Monitor Management** - Create and manage website monitors
- **Optimization Suggestions** - Actionable performance insights

## 🆓 Free API Benefits

| Feature | Traditional Cost | Our Solution |
|---------|------------------|--------------|
| Performance Analysis | $50-200/month | **FREE** |
| Uptime Monitoring | $10-50/month | **FREE** |
| AI Insights | $100-500/month | **FREE** |
| **Total Savings** | **$160-750/month** | **$0** |

## 🚀 Quick Start

### 1. Get Free API Keys (No Credit Card Required)

```bash
# Google PageSpeed (Optional but Recommended)
# Visit: https://console.cloud.google.com/
# Enable: PageSpeed Insights API

# UptimeRobot (Required for monitoring)  
# Visit: https://uptimerobot.com/
# Free: 50 monitors, 5-minute checks

# Groq (Required for AI)
# Visit: https://console.groq.com/
# Free: 1,000 requests/day
```

### 2. Setup Environment

```bash
# MCP Server
cd mcp-server
cp .env.example .env
# Add your API keys

# Agent Backend  
cd agent-backend
cp .env.example .env
# Add your API keys

# Frontend
cd frontend
npm install
```

### 3. Run Application

```bash
# Windows
.\start-dev.ps1

# Mac/Linux  
./start-dev.sh
```

Access at http://localhost:3000

## 💡 Sample Marketing Queries

```text
"Analyze the performance of nike.com"
"Check uptime for amazon.com" 
"Create a monitor for tesla.com"
"Performance insights for facebook.com"
"Optimize my website speed"
```

## 📊 Available Tools

### Website Performance
- **Performance Score**: Core Web Vitals analysis
- **Mobile/Desktop**: Both device strategies
- **Optimization**: Actionable improvement suggestions

### Uptime Monitoring  
- **Real-time Status**: Website availability tracking
- **Monitor Creation**: Automated monitoring setup
- **Historical Data**: Uptime statistics and logs

### AI Insights
- **Natural Language**: Conversational interface
- **Smart Analysis**: Multi-tool coordination
- **Strategic Recommendations**: Marketing optimization tips

## 🔧 Technical Architecture

```
Frontend (Next.js) → Agent Backend (FastAPI + Groq) → MCP Server → Free APIs
```

- **Frontend**: React/Next.js with modern UI
- **Backend**: Python FastAPI with LangChain
- **MCP Server**: Node.js with standardized tool interface
- **APIs**: Google PageSpeed, UptimeRobot, Groq LLM

## 📈 Rate Limits (Free Tiers)

| API | Free Limit | Usage |
|-----|------------|-------|
| Google PageSpeed | ~100/hour | Performance analysis |
| UptimeRobot | 10 req/min | Monitoring |
| Groq | 1,000 req/day | AI insights |

## 🎯 Perfect For

- **Startups** - Professional analytics without budget
- **Developers** - Learning modern AI architectures  
- **Marketers** - Actionable website insights
- **Agencies** - Client monitoring dashboards
- **Students** - Real-world AI applications

## 📚 Documentation

- **[FREE_API_SETUP.md](./FREE_API_SETUP.md)** - Detailed setup guide
- **[MARKETING_SETUP.md](./MARKETING_SETUP.md)** - Marketing use cases
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Technical architecture

## 🛠️ Development

```bash
# Start all services
.\start-dev.ps1  # Windows
./start-dev.sh   # Mac/Linux

# Individual services
cd mcp-server && npm run dev      # Port 3001
cd agent-backend && python app.py # Port 8000  
cd frontend && npm run dev         # Port 3000
```

## 🌟 Why This Application

1. **Cost Effective**: $0 vs $160-750/month alternatives
2. **Professional**: Enterprise-level features
3. **Educational**: Learn modern AI architectures
4. **Practical**: Real marketing value
5. **Scalable**: Upgrade path to paid tiers if needed

## 🤝 Contributing

This is a demonstration of modern AI application development using free APIs. Perfect for learning, prototyping, and small-scale production use.

## 📞 Support

All APIs used have:
- ✅ Free tiers available
- ✅ No credit card required  
- ✅ Professional documentation
- ✅ Active communities

---

**Stop paying for marketing analytics!** 🚀  
Get professional insights with our free AI-powered solution.
