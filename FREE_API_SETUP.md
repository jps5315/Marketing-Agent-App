# Marketing Agent Application - Free API Setup Guide

## Overview

This marketing analytics application uses **completely free APIs** - no credit card required! Perfect for developers and marketers who want professional insights without paid subscriptions.

## Free APIs Used

### 1. Google PageSpeed Insights API
- **Cost**: 100% FREE
- **Rate Limit**: Generous (no strict limits without API key)
- **Features**: Performance analysis, optimization suggestions
- **Setup**: Optional API key (recommended for higher limits)

### 2. UptimeRobot API
- **Cost**: FREE tier available
- **Rate Limit**: 10 requests/minute (free tier)
- **Features**: Website monitoring, uptime tracking
- **Setup**: Requires free account

### 3. Groq LLM API
- **Cost**: FREE tier available
- **Rate Limit**: 1,000 requests/day, 6,000 tokens/minute
- **Features**: Fast Llama 3.1 models
- **Setup**: Requires free account

## Quick Setup Guide

### Step 1: Get Free API Keys

#### Google PageSpeed Insights (Optional but Recommended)
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable "PageSpeed Insights API"
4. Create API credentials
5. **No billing required** for moderate usage

#### UptimeRobot (Required for monitoring)
1. Visit [UptimeRobot](https://uptimerobot.com/)
2. Sign up for FREE account
3. Go to "Integrations & API" in sidebar
4. Create API key
5. **Free tier includes**: 50 monitors, 5-minute checks

#### Groq (Required for AI)
1. Visit [Groq Console](https://console.groq.com/)
2. Sign up for FREE account
3. Create API key
4. **Free tier includes**: 1,000 requests/day

### Step 2: Configure Environment

#### MCP Server Setup
```bash
cd mcp-server
copy .env.example .env  # Windows
# or
cp .env.example .env     # Mac/Linux
```

Edit `.env`:
```env
# Google PageSpeed API Key (optional)
GOOGLE_PAGESPEED_API_KEY=your_google_api_key_here

# UptimeRobot API Key (required for monitoring)
UPTIMEROBOT_API_KEY=your_uptimerobot_api_key_here
```

#### Agent Backend Setup
```bash
cd agent-backend
copy .env.example .env  # Windows
# or
cp .env.example .env     # Mac/Linux
```

Edit `.env`:
```env
# Groq API Key (required)
GROQ_API_KEY=your_groq_api_key_here

# Google PageSpeed API Key (optional)
GOOGLE_PAGESPEED_API_KEY=your_google_api_key_here

# UptimeRobot API Key (required)
UPTIMEROBOT_API_KEY=your_uptimerobot_api_key_here
```

### Step 3: Install Dependencies

#### Frontend Dependencies
```bash
cd frontend
npm install
```

#### Backend Dependencies
```bash
cd agent-backend
pip install -r requirements.txt
```

#### MCP Server Dependencies
```bash
cd mcp-server
npm install
```

### Step 4: Run Application

#### Option 1: Use Startup Script
```bash
# Windows
.\start-dev.ps1

# Mac/Linux
./start-dev.sh
```

#### Option 2: Manual Start
Open 3 terminal windows:

**Terminal 1 - MCP Server:**
```bash
cd mcp-server
npm run dev
```

**Terminal 2 - Agent Backend:**
```bash
cd agent-backend
python app.py
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

## What You Can Do For Free

### Website Performance Analysis
```text
"Analyze the performance of nike.com"
"Check mobile performance for amazon.com"
"Performance insights for my website"
```

### Uptime Monitoring
```text
"Check uptime for google.com"
"Create a monitor for facebook.com"
"Show all my monitors"
```

### AI-Powered Insights
```text
"Optimize my website performance"
"Marketing recommendations for tesla.com"
"How to improve my website speed"
```

## API Rate Limits (Free Tiers)

| API | Free Limit | What You Get |
|-----|------------|--------------|
| Google PageSpeed | ~100/hour | Performance scores, optimization suggestions |
| UptimeRobot | 10 req/min | Website monitoring, uptime tracking |
| Groq | 1,000 req/day | AI-powered insights and recommendations |

## Troubleshooting Free API Issues

### Google PageSpeed Issues
- **No API key needed**: Works without key for testing
- **Rate limits**: Wait a few minutes between requests
- **Invalid URLs**: Must include https:// (e.g., https://example.com)

### UptimeRobot Issues
- **Account required**: Must create free account
- **API key location**: Dashboard → Integrations & API → API
- **Rate limits**: 10 requests per minute

### Groq Issues
- **Account verification**: Email may need verification
- **Rate limits**: 1,000 requests per day
- **Model availability**: Llama 3.1 models included

## Sample Marketing Queries

### Performance Analysis
```text
"Analyze nike.com performance"
"Check mobile speed for amazon.com"
"Performance score for apple.com"
"Optimize my website speed"
```

### Monitoring Setup
```text
"Create monitor for tesla.com"
"Check uptime of facebook.com"
"Show all my monitors"
"Monitor my website uptime"
```

### AI Recommendations
```text
"How to improve my website performance"
"Marketing optimization tips"
"SEO recommendations for my site"
"User experience improvements"
```

## Cost Comparison

| Feature | This App | Paid Alternatives |
|---------|-----------|-------------------|
| Performance Analysis | FREE | $50-200/month |
| Uptime Monitoring | FREE | $10-50/month |
| AI Insights | FREE | $100-500/month |
| **Total Savings** | **$0** | **$160-750/month** |

## Professional Features (Free)

- **Real-time data**: Live performance metrics
- **AI analysis**: Llama 3.1 powered insights
- **Monitoring**: Automated uptime tracking
- **Optimization**: Actionable recommendations
- **No credit card**: Completely free setup

## Next Steps

1. **Test the application**: Try sample queries
2. **Monitor your sites**: Set up uptime monitoring
3. **Optimize performance**: Use AI recommendations
4. **Scale up**: Upgrade to paid tiers if needed

## Support

All APIs used in this application have:
- ✅ Free tiers available
- ✅ No credit card required
- ✅ Generous rate limits
- ✅ Professional documentation
- ✅ Active communities

## Why This Works

This application demonstrates that **professional marketing analytics** don't require expensive subscriptions. By combining:

1. **Google's free PageSpeed API** for performance data
2. **UptimeRobot's free monitoring** for reliability tracking  
3. **Groq's free LLM** for intelligent insights

You get enterprise-level capabilities at zero cost!

Perfect for:
- 🚀 Startups and small businesses
- 👨‍💻 Developers and marketers
- 📈 Marketing agencies
- 🎓 Students and learners
- 💼 Freelancers and consultants
