# AI Assistant with Angular, Spring Boot, LangChain, and Qdrant

A comprehensive AI assistant application with the following architecture:

```
User → Angular UI → Spring Boot API → LangChain Pipeline → Vector DB (Qdrant) + LiteLLM → LLM (OpenAI/Claude)
```

## Project Structure

- `frontend/` - Angular application with chat interface
- `backend/` - Spring Boot REST API
- `langchain-service/` - Python service with LangChain pipeline
- `docker/` - Docker configuration for all services

## Quick Start

1. Start all services with Docker Compose:
```bash
cd docker
docker-compose up -d
```

2. Access the application:
- Frontend: http://localhost:4200
- Backend API: http://localhost:8080
- LangChain Service: http://localhost:8000
- Qdrant Dashboard: http://localhost:6333/dashboard

## Services

### Frontend (Angular)
- Modern chat interface
- Real-time messaging
- TypeScript with Angular Material

### Backend (Spring Boot)
- REST API endpoints
- Request routing to LangChain service
- CORS configuration for Angular

### LangChain Service (Python)
- Vector database integration with Qdrant
- LiteLLM for multi-provider LLM access
- Context retrieval and augmented generation

### Vector Database (Qdrant)
- Document storage and similarity search
- REST API for vector operations
- Web dashboard for management

## Environment Variables

Create `.env` files in each service directory with required API keys and configuration.