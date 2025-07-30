#!/bin/bash

echo "🧪 Testing AI Assistant Setup..."

# Test Maven wrapper
echo "Testing Maven wrapper..."
cd backend
if ./mvnw --version > /dev/null 2>&1; then
    echo "✅ Maven wrapper is working"
else
    echo "❌ Maven wrapper failed"
    exit 1
fi
cd ..

# Test Node.js setup (if available)
echo "Testing Node.js setup..."
cd frontend
if command -v npm > /dev/null 2>&1; then
    if npm --version > /dev/null 2>&1; then
        echo "✅ Node.js/npm is available"
    else
        echo "⚠️  npm not working properly"
    fi
else
    echo "ℹ️  Node.js not installed (will use Docker)"
fi
cd ..

# Test Python setup (if available)
echo "Testing Python setup..."
cd langchain-service
if command -v python3 > /dev/null 2>&1; then
    if python3 --version > /dev/null 2>&1; then
        echo "✅ Python 3 is available"
    else
        echo "⚠️  Python 3 not working properly"
    fi
else
    echo "ℹ️  Python 3 not installed (will use Docker)"
fi
cd ..

# Test Docker
echo "Testing Docker..."
if command -v docker > /dev/null 2>&1; then
    if docker --version > /dev/null 2>&1; then
        echo "✅ Docker is available"
    else
        echo "❌ Docker not working properly"
        exit 1
    fi
else
    echo "❌ Docker not installed - required for running the application"
    exit 1
fi

# Test Docker Compose
echo "Testing Docker Compose..."
if command -v docker-compose > /dev/null 2>&1; then
    if docker-compose --version > /dev/null 2>&1; then
        echo "✅ Docker Compose is available"
    else
        echo "❌ Docker Compose not working properly"
        exit 1
    fi
else
    echo "❌ Docker Compose not installed - required for running the application"
    exit 1
fi

# Check environment file
echo "Checking environment configuration..."
if [ -f "docker/.env" ]; then
    echo "✅ Environment file exists"
    if grep -q "OPENAI_API_KEY=your_openai_api_key_here" docker/.env || grep -q "ANTHROPIC_API_KEY=your_anthropic_api_key_here" docker/.env; then
        echo "⚠️  Please update your API keys in docker/.env"
    else
        echo "✅ Environment file appears to be configured"
    fi
else
    echo "⚠️  Environment file missing. Run: cd docker && cp .env.example .env"
fi

echo ""
echo "🎯 Setup Test Complete!"
echo ""
echo "Next steps:"
echo "1. Configure API keys: cd docker && cp .env.example .env && nano .env"
echo "2. Start the application: ./start.sh"