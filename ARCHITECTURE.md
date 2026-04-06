# Weather Agent Application - Architecture Documentation

## System Architecture

This application demonstrates a modern, agent-driven architecture with clear separation of concerns and standardized interfaces.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  Agent Backend  │    │   MCP Server    │    │ OpenWeatherMap  │
│   (Next.js)     │◄──►│  (FastAPI)      │◄──►│   (Node.js)     │◄──►│     API         │
│                 │    │                 │    │                 │    │                 │
│ - React UI      │    │ - LangChain     │    │ - MCP Protocol  │    │ - Weather Data  │
│ - User Input    │    │ - OpenAI LLM    │    │ - API Wrapper   │    │ - Forecasts     │
│ - Chat Interface│    │ - Tool Calling  │    │ - Error Handling│    │ - Air Quality   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
       HTTP/JSON              MCP Protocol              REST API
     Port 3000               Port 3001                External
```

## Component Details

### 1. Frontend (Next.js + React)
**Location**: `/frontend/`

**Technologies**:
- Next.js 14 with App Router
- React 18 with TypeScript
- Tailwind CSS for styling
- Lucide React for icons
- Axios for HTTP requests

**Responsibilities**:
- User interface and interaction
- Real-time chat experience
- Message history management
- Responsive design
- Error handling and user feedback

**Key Features**:
- Conversational interface
- Sample question suggestions
- Loading states and animations
- Mobile-responsive design
- Auto-scrolling chat

### 2. Agent Backend (FastAPI + LangChain)
**Location**: `/agent-backend/`

**Technologies**:
- FastAPI for REST API
- LangChain for LLM orchestration
- OpenAI GPT-3.5-turbo for reasoning
- Python async/await for concurrency
- MCP client integration

**Responsibilities**:
- Natural language understanding
- Tool selection and execution
- Response generation
- MCP server communication
- Session management

**Key Features**:
- OpenAI Functions Agent
- Dynamic tool loading from MCP
- Async request handling
- Error recovery
- Health check endpoints

### 3. MCP Server (Node.js)
**Location**: `/mcp-server/`

**Technologies**:
- Model Context Protocol (MCP) SDK
- Node.js with ES modules
- Axios for HTTP requests
- OpenWeatherMap API integration

**Responsibilities**:
- Standardized tool interface
- Weather API abstraction
- Error handling and validation
- Protocol compliance
- Resource management

**Available Tools**:
- `get_current_weather`: Current conditions
- `get_weather_forecast`: 5-day forecasts
- `get_air_pollution`: Air quality data

## Data Flow

### 1. User Query Flow
```
User Input → Frontend → Agent Backend → LLM → Tool Selection → MCP Server → Weather API → Response Chain
```

**Step-by-step**:
1. User types message in frontend
2. Frontend sends POST to `/chat` endpoint
3. Agent Backend receives request
4. LangChain agent processes with OpenAI LLM
5. LLM determines if tools are needed
6. MCP client calls appropriate tool
7. MCP Server makes API call to OpenWeatherMap
8. Response flows back through chain
9. LLM generates natural language response
10. Frontend displays response to user

### 2. Tool Calling Flow
```
Agent Backend → MCP Client → MCP Server → OpenWeatherMap API → MCP Server → MCP Client → Agent Backend
```

**MCP Protocol Benefits**:
- Standardized tool interface
- Language-agnostic communication
- Automatic tool discovery
- Type safety and validation
- Error handling standardization

## Key Design Patterns

### 1. Microservices Architecture
- Each component is independently deployable
- Clear service boundaries
- Technology diversity (Node.js, Python, React)
- Scalable and maintainable

### 2. Agent-First Design
- LLM as the central reasoning engine
- Tools as extensions of agent capabilities
- Natural language as primary interface
- Dynamic tool selection

### 3. Protocol Standardization
- MCP for tool interfaces
- REST for service communication
- JSON for data serialization
- HTTP for transport layer

## Error Handling Strategy

### Frontend Error Handling
- Network request timeouts
- User input validation
- Loading state management
- Graceful degradation

### Backend Error Handling
- API key validation
- MCP server connectivity
- Tool execution failures
- LLM API rate limits

### MCP Server Error Handling
- External API failures
- Invalid location names
- Rate limit handling
- Data validation

## Security Considerations

### API Key Management
- Environment variables for keys
- No hardcoded credentials
- Server-side key storage
- Regular key rotation

### Network Security
- Local development only
- CORS configuration
- Input validation
- Error message sanitization

## Performance Optimizations

### Frontend Optimizations
- React.memo for component memoization
- Efficient state management
- Lazy loading considerations
- Bundle size optimization

### Backend Optimizations
- Async/await for concurrency
- Connection pooling
- Response caching
- Efficient JSON parsing

### MCP Server Optimizations
- Request batching
- Response caching
- Minimal data transfer
- Error response optimization

## Monitoring and Observability

### Logging Strategy
- Structured logging
- Request tracing
- Error categorization
- Performance metrics

### Health Checks
- Frontend: Basic connectivity
- Backend: Service health and MCP connectivity
- MCP Server: API availability and tool functionality

## Future Enhancements

### Potential Improvements
1. **Authentication**: User accounts and sessions
2. **Caching**: Redis for response caching
3. **Monitoring**: Prometheus metrics and Grafana dashboards
4. **Testing**: Comprehensive unit and integration tests
5. **Deployment**: Docker containers and Kubernetes
6. **Security**: HTTPS, authentication, rate limiting
7. **Features**: Location services, weather alerts, historical data

### Scalability Considerations
- Horizontal scaling of backend services
- Load balancing for frontend
- Database for user preferences
- Message queue for async processing

## Development Workflow

### Local Development
1. Start MCP Server first
2. Start Agent Backend
3. Start Frontend
4. Test end-to-end functionality

### Testing Strategy
- Unit tests for individual components
- Integration tests for service communication
- End-to-end tests for user workflows
- Load testing for performance validation

This architecture demonstrates modern software development practices with clear separation of concerns, standardized interfaces, and agent-driven design patterns.
