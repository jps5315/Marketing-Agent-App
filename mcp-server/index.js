import express from 'express';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

class SimpleHTTPServer {
  constructor() {
    this.app = express();
    this.app.use(express.json());
    this.setupRoutes();
  }

  setupRoutes() {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({ status: 'healthy', service: 'mcp-http-server' });
    });

    // Root endpoint
    this.app.get('/', (req, res) => {
      res.json({
        service: 'Marketing MCP HTTP Server',
        version: '1.0.0',
        endpoints: {
          health: '/health',
          list_tools: '/list_tools',
          call_tool: '/call_tool'
        }
      });
    });

    // List tools
    this.app.get('/list_tools', (req, res) => {
      const tools = [
        {
          name: 'get_website_performance',
          description: 'Get website performance metrics using Google PageSpeed Insights',
          inputSchema: {
            type: 'object',
            properties: {
              url: {
                type: 'string',
                description: 'Website URL (e.g., "https://example.com")',
              },
              strategy: {
                type: 'string',
                enum: ['mobile', 'desktop'],
                description: 'Device strategy (default: desktop)',
                default: 'mobile',
              },
            },
            required: ['url'],
          },
        },
        {
          name: 'get_website_uptime',
          description: 'Check website uptime using UptimeRobot API',
          inputSchema: {
            type: 'object',
            properties: {
              url: {
                type: 'string',
                description: 'Website URL to check',
              },
              friendly_name: {
                type: 'string',
                description: 'Friendly name for the monitor',
              },
            },
            required: ['url'],
          },
        },
        {
          name: 'create_monitor',
          description: 'Create a new uptime monitor using UptimeRobot API',
          inputSchema: {
            type: 'object',
            properties: {
              url: {
                type: 'string',
                description: 'Website URL to monitor',
              },
              friendly_name: {
                type: 'string',
                description: 'Friendly name for the monitor',
              },
              type: {
                type: 'string',
                description: 'Monitor type (1=HTTP)',
                default: '1',
              },
              interval: {
                type: 'number',
                description: 'Check interval in seconds (300=5 minutes)',
                default: 300,
              },
            },
            required: ['url', 'friendly_name'],
          },
        },
        {
          name: 'get_all_monitors',
          description: 'Get all uptime monitors from UptimeRobot',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
      ];
      
      res.json({ tools });
    });

    // Call tool
    this.app.post('/call_tool', async (req, res) => {
      try {
        const { name, arguments: args } = req.body;
        
        console.log(`🔧 Tool Call Received:`, { name, arguments: args });
        
        if (!name) {
          console.error('❌ No tool name provided');
          return res.status(400).json({ error: 'Tool name is required' });
        }

        let result;
        console.log(`🎯 Executing tool: ${name}`);
        
        switch (name) {
          case 'get_website_performance':
            console.log('✅ Tool matched: get_website_performance');
            result = await this.getWebsitePerformance(args);
            break;
          case 'get_website_uptime':
            console.log('✅ Tool matched: get_website_uptime');
            result = await this.getWebsiteUptime(args);
            break;
          case 'create_monitor':
            console.log('✅ Tool matched: create_monitor');
            result = await this.createMonitor(args);
            break;
          case 'get_all_monitors':
            console.log('✅ Tool matched: get_all_monitors');
            result = await this.getAllMonitors();
            break;
          default:
            console.error(`❌ Unknown tool: ${name}`);
            console.error(`🔧 Available tools: get_website_performance, get_website_uptime, create_monitor, get_all_monitors`);
            throw new Error(`Unknown tool: ${name}`);
        }

        console.log(`✅ Tool execution completed for: ${name}`);
        res.json(result);
      } catch (error) {
        console.error('Tool execution error details:', {
          message: error.message,
          status: error.response?.status,
          statusText: error.response?.statusText,
          url: error.config?.url,
          method: error.config?.method
        });
        
        if (error.response?.status === 404) {
          console.error('404 Error - API endpoint not found:', error.config?.url);
        }
        
        throw new Error(`Tool execution error: ${error.message}`);
      }
    });
  }

  async getWebsitePerformance(args) {
    const { url, strategy = 'mobile' } = args;
    
    console.log(`🔍 getWebsitePerformance called with:`, { url, strategy });
    
    try {
      const apiKey = process.env.GOOGLE_PAGESPEED_API_KEY;
      const apiUrl = `https://www.googleapis.com/pagespeedonline/v5/runPagespeed`;
      
      let requestUrl = `${apiUrl}?url=${encodeURIComponent(url)}&strategy=${strategy}`;
      if (apiKey) {
        requestUrl += `&key=${apiKey}`;
      }

      console.log(`📊 Making PageSpeed API call to: ${requestUrl}`);
      console.log(`🔑 API Key Present: ${!!apiKey}`);
      
      const response = await axios.get(requestUrl, { timeout: 6000000 }); // 100 minutes (6,000,000ms)
      
      console.log(`📡 PageSpeed API Response Status: ${response.status}`);
      console.log(`📡 PageSpeed API Response Headers:`, response.headers);
      console.log(`📡 PageSpeed API Full Response Data:`, JSON.stringify(response.data, null, 2));
      
      // Log specific parts of the response
      const data = response.data;
      console.log(`🔍 Lighthouse Result Present:`, !!data.lighthouseResult);
      console.log(`🔍 Categories Present:`, !!data.lighthouseResult?.categories);
      console.log(`🔍 Performance Score:`, data.lighthouseResult?.categories?.performance?.score);
      console.log(`🔍 Audits Count:`, Object.keys(data.lighthouseResult?.audits || {}).length);
      console.log(`🔍 Loading Experience:`, !!data.loadingExperience);
      console.log(`🔍 Origin Loading Experience:`, !!data.originLoadingExperience);
      
      // Extract key metrics
      const metrics = {
        performance_score: Math.round(data.lighthouseResult?.categories?.performance?.score * 100) || 0,
        first_contentful_paint: data.lighthouseResult?.audits?.['first-contentful-paint']?.numericValue || 0,
        largest_contentful_paint: data.lighthouseResult?.audits?.['largest-contentful-paint']?.numericValue || 0,
        cumulative_layout_shift: data.lighthouseResult?.audits?.['cumulative-layout-shift']?.numericValue || 0,
        total_blocking_time: data.lighthouseResult?.audits?.['total-blocking-time']?.numericValue || 0,
      };

      console.log(`📊 Extracted Metrics:`, metrics);

      // Extract opportunities
      const opportunities = Object.values(data.lighthouseResult?.audits || {})
        .filter(audit => audit.id && audit.title && audit.score < 1)
        .slice(0, 5)
        .map(audit => ({
          id: audit.id,
          title: audit.title,
          description: audit.description,
          impact: audit.scoreDisplayMode === 'numeric' ? (1 - audit.score) * 100 : 0
        }));

      console.log(`🎯 Opportunities Found:`, opportunities.length);
      console.log(`🎯 Top Opportunities:`, opportunities.map(opp => opp.title));

      const result = {
        url,
        strategy,
        timestamp: new Date().toISOString(),
        performance_score: metrics.performance_score,
        metrics,
        opportunities,
        loading_experience: data.loadingExperience?.metrics || {},
        origin_loading_experience: data.originLoadingExperience?.metrics || {},
      };

      console.log(`✅ Final Result:`, JSON.stringify(result, null, 2));

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      console.error('PageSpeed API error:', error.message);
      throw new Error(`PageSpeed API error: ${error.message}`);
    }
  }

  async getWebsiteUptime(args) {
    const { url, friendly_name } = args;
    
    try {
      const apiKey = process.env.UPTIMEROBOT_API_KEY;
      if (!apiKey) {
        throw new Error('UPTIMEROBOT_API_KEY environment variable is required');
      }

      // First, try to find existing monitor
      const monitorsResponse = await axios.post('https://api.uptimerobot.com/v2/getMonitors', {
        api_key: apiKey,
        format: 'json',
        search: url
      });

      const monitors = monitorsResponse.data.monitors;
      
      if (monitors && monitors.length > 0) {
        const monitor = monitors[0];
        const result = {
          url,
          monitor_id: monitor.id,
          status: monitor.status,
          uptime: monitor.custom_uptime_ratio,
          response_time: monitor.response_time,
          logs: monitor.logs || [],
          timestamp: new Date().toISOString(),
        };

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      } else {
        // No monitor found
        const result = {
          url,
          message: `No monitor found for ${url}. Would you like to create one?`,
          timestamp: new Date().toISOString(),
        };

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }
    } catch (error) {
      console.error('UptimeRobot API error:', error.message);
      throw new Error(`UptimeRobot API error: ${error.message}`);
    }
  }

  async createMonitor(args) {
    const { url, friendly_name, type = '1', interval = 300 } = args;
    
    try {
      const apiKey = process.env.UPTIMEROBOT_API_KEY;
      if (!apiKey) {
        throw new Error('UPTIMEROBOT_API_KEY environment variable is required');
      }

      const response = await axios.post('https://api.uptimerobot.com/v2/newMonitor', {
        api_key: apiKey,
        format: 'json',
        type,
        url,
        friendly_name,
        interval,
      });

      const result = {
        url,
        friendly_name,
        monitor_id: response.data.monitor?.id,
        success: !!response.data.monitor?.id,
        message: response.data.stat === 'ok' ? 'Monitor created successfully' : 'Failed to create monitor',
        timestamp: new Date().toISOString(),
      };

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`UptimeRobot API error: ${error.message}`);
    }
  }

  async start(port = 3001) {
    try {
      this.app.listen(port, () => {
        console.log(`MCP HTTP Server running on port ${port}`);
        console.log(`Health check: http://localhost:${port}/health`);
        console.log(`List tools: http://localhost:${port}/list_tools`);
        console.log(`Call tool: http://localhost:${port}/call_tool`);
      });
    } catch (error) {
      console.error('Failed to start MCP HTTP Server:', error);
      process.exit(1);
    }
  }
}

// Start the server
console.log('Uptime Robot API key present:', !!process.env.UPTIMEROBOT_API_KEY);
console.log('Google Pagespeed API key present:', !!process.env.GOOGLE_PAGESPEED_API_KEY);
const server = new SimpleHTTPServer();
server.start(3001).catch(console.error);
