#!/bin/bash

echo "🚀 Starting AI Assistant System..."

# Check if .env file exists
if [ ! -f "docker/.env" ]; then
    echo "⚠️  .env file not found. Please copy docker/.env.example to docker/.env and configure your API keys."
    echo "   cd docker && cp .env.example .env"
    echo "   Then edit .env with your OpenAI/Anthropic API keys."
    exit 1
fi

# Navigate to docker directory
cd docker

echo "📦 Building and starting services with Docker Compose..."

# Build and start all services
docker-compose up --build -d

echo "⏳ Waiting for services to be ready..."

# Wait for services to be healthy
echo "   Waiting for Qdrant..."
until curl -s http://localhost:6333/health > /dev/null; do
    sleep 2
done
echo "   ✅ Qdrant is ready"

echo "   Waiting for LangChain service..."
until curl -s http://localhost:8000/health > /dev/null; do
    sleep 2
done
echo "   ✅ LangChain service is ready"

echo "   Waiting for Spring Boot backend..."
until curl -s http://localhost:8080/api/chat/health > /dev/null; do
    sleep 2
done
echo "   ✅ Spring Boot backend is ready"

echo "   Waiting for Angular frontend..."
until curl -s http://localhost:4200 > /dev/null; do
    sleep 2
done
echo "   ✅ Angular frontend is ready"

echo ""
echo "🎉 AI Assistant is now running!"
echo ""
echo "📱 Access the application:"
echo "   Frontend: http://localhost:4200"
echo "   Backend API: http://localhost:8080/api"
echo "   LangChain Service: http://localhost:8000"
echo "   Qdrant Dashboard: http://localhost:6333/dashboard"
echo ""
echo "📚 To load sample data into the vector database:"
echo "   docker exec -it ai-assistant-langchain python scripts/load_sample_data.py"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose down"
echo ""
echo "📋 To view logs:"
echo "   docker-compose logs -f [service-name]"
echo "   Services: qdrant, langchain-service, backend, frontend"