# AI Assistant Development Guide

## Architecture Overview

This AI assistant implements a complete RAG (Retrieval-Augmented Generation) pipeline with the following components:

```
User → Angular UI → Spring Boot API → LangChain Service → Qdrant Vector DB + LiteLLM → LLM
```

## Technology Stack

### Frontend (Angular)
- **Framework**: Angular 17 with standalone components
- **UI Library**: Angular Material
- **Features**: Real-time chat interface, message history, loading states
- **Port**: 4200

### Backend (Spring Boot)
- **Framework**: Spring Boot 3.2 with Java 17
- **Database**: H2 (in-memory) for conversation history
- **Features**: REST API, CORS configuration, request validation
- **Port**: 8080

### LangChain Service (Python)
- **Framework**: FastAPI with Python 3.11
- **Libraries**: LangChain, LiteLLM, Sentence Transformers
- **Features**: RAG pipeline, vector search, multi-provider LLM support
- **Port**: 8000

### Vector Database (Qdrant)
- **Database**: Qdrant vector database
- **Features**: Similarity search, document storage, web dashboard
- **Ports**: 6333 (HTTP), 6334 (gRPC)

## Development Setup

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local Angular development)
- Java 17+ (for local Spring Boot development)
- Python 3.11+ (for local LangChain development)

### Quick Start
1. Clone the repository
2. Copy environment variables: `cd docker && cp .env.example .env`
3. Add your API keys to `docker/.env`
4. Run: `./start.sh`

### Local Development

#### Frontend Development
```bash
cd frontend
npm install
npm start
# Runs on http://localhost:4200
```

#### Backend Development
```bash
cd backend
./mvnw spring-boot:run
# Runs on http://localhost:8080
```

#### LangChain Service Development
```bash
cd langchain-service
pip install -r requirements.txt
python main.py
# Runs on http://localhost:8000
```

## API Documentation

### Spring Boot API

#### POST /api/chat/message
Send a chat message and get AI response.

**Request:**
```json
{
  "message": "What is artificial intelligence?",
  "conversationId": "uuid-string"
}
```

**Response:**
```json
{
  "response": "AI response text",
  "conversationId": "uuid-string",
  "sources": ["doc-id-1", "doc-id-2"],
  "success": true
}
```

#### GET /api/chat/history/{conversationId}
Get conversation history for a specific conversation.

### LangChain Service API

#### POST /chat
Process chat request with RAG pipeline.

**Request:**
```json
{
  "query": "User question",
  "conversation_id": "uuid-string"
}
```

#### POST /documents
Add document to vector database.

**Request:**
```json
{
  "content": "Document content",
  "metadata": {"title": "Doc title", "category": "tech"}
}
```

## Configuration

### Environment Variables

#### LangChain Service (.env)
- `OPENAI_API_KEY`: OpenAI API key for GPT models
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude models
- `LITELLM_MODEL`: Model to use (gpt-3.5-turbo, claude-3-sonnet-20240229, etc.)
- `QDRANT_HOST`: Qdrant host (default: localhost)
- `QDRANT_PORT`: Qdrant port (default: 6333)
- `EMBEDDING_MODEL`: Sentence transformer model (default: all-MiniLM-L6-v2)

#### Spring Boot (application.yml)
- `langchain.service.url`: URL of LangChain service
- `cors.allowed-origins`: Allowed CORS origins

## Data Flow

1. **User Input**: User types message in Angular UI
2. **API Call**: Angular sends POST request to Spring Boot `/api/chat/message`
3. **Persistence**: Spring Boot saves user message to H2 database
4. **LangChain Request**: Spring Boot forwards request to LangChain service `/chat`
5. **Vector Search**: LangChain service searches Qdrant for relevant documents
6. **LLM Generation**: LangChain service calls LiteLLM with context and query
7. **Response Chain**: Response flows back through the same chain
8. **UI Update**: Angular displays the AI response

## Adding New Features

### Adding New LLM Providers
1. Update `LITELLM_MODEL` environment variable
2. Add corresponding API key environment variable
3. LiteLLM automatically handles the provider routing

### Adding New Document Types
1. Extend the `DocumentRequest` model in LangChain service
2. Update the vector service to handle new metadata fields
3. Modify the embedding and retrieval logic if needed

### Extending the UI
1. Add new Angular components in `frontend/src/app/`
2. Update routing in `app.routes.ts`
3. Add new API endpoints in Spring Boot if needed

## Troubleshooting

### Common Issues

1. **Services not starting**: Check Docker logs with `docker-compose logs [service-name]`
2. **API key errors**: Verify environment variables in `docker/.env`
3. **Vector search not working**: Ensure Qdrant is running and documents are loaded
4. **CORS issues**: Check Spring Boot CORS configuration

### Debugging

#### View Service Logs
```bash
docker-compose logs -f langchain-service
docker-compose logs -f backend
docker-compose logs -f frontend
```

#### Access Service Containers
```bash
docker exec -it ai-assistant-langchain bash
docker exec -it ai-assistant-backend bash
```

#### Check Service Health
```bash
curl http://localhost:6333/health  # Qdrant
curl http://localhost:8000/health  # LangChain
curl http://localhost:8080/api/chat/health  # Spring Boot
```

## Testing

### Load Sample Data
```bash
docker exec -it ai-assistant-langchain python scripts/load_sample_data.py
```

### Test API Endpoints
```bash
# Test Spring Boot API
curl -X POST http://localhost:8080/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "What is AI?", "conversationId": "test-123"}'

# Test LangChain Service
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?"}'
```

## Performance Considerations

- **Vector Search**: Adjust `score_threshold` and `limit` parameters for optimal results
- **LLM Calls**: Configure `max_tokens` and `temperature` based on use case
- **Caching**: Consider adding Redis for conversation history in production
- **Scaling**: Use Docker Swarm or Kubernetes for horizontal scaling