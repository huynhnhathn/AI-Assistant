import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

from app.chat_service import ChatService
from app.vector_service import VectorService
from app.llm_service import LLMService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Assistant LangChain Service",
    description="LangChain service with Qdrant vector database and LiteLLM integration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None
    conversation_id: Optional[str] = None

class DocumentRequest(BaseModel):
    content: str
    metadata: Optional[dict] = None

# Initialize services
vector_service = VectorService()
llm_service = LLMService()
chat_service = ChatService(vector_service, llm_service)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        await vector_service.initialize()
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

@app.get("/")
async def root():
    return {"message": "AI Assistant LangChain Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "langchain-service"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat request with RAG pipeline"""
    try:
        logger.info(f"Processing chat request for conversation: {request.conversation_id}")
        
        response = await chat_service.process_query(
            query=request.query,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(
            response=response["answer"],
            sources=response.get("sources", []),
            conversation_id=request.conversation_id
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents")
async def add_document(request: DocumentRequest):
    """Add document to vector database"""
    try:
        doc_id = await vector_service.add_document(
            content=request.content,
            metadata=request.metadata or {}
        )
        return {"message": "Document added successfully", "document_id": doc_id}
        
    except Exception as e:
        logger.error(f"Error adding document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/count")
async def get_document_count():
    """Get total number of documents in vector database"""
    try:
        count = await vector_service.get_document_count()
        return {"document_count": count}
        
    except Exception as e:
        logger.error(f"Error getting document count: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("SERVICE_PORT", "8000"))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )