import logging
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import ResponseHandlingException
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from .config import config

logger = logging.getLogger(__name__)

class QdrantVectorStore:
    """Qdrant vector database integration for RAG application"""
    
    def __init__(self):
        self.client = None
        self.embeddings = None
        self.vector_store = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Qdrant client and embeddings"""
        try:
            # Initialize Qdrant client
            self.client = QdrantClient(
                url=config.QDRANT_URL,
                api_key=config.QDRANT_API_KEY
            )
            
            # Initialize OpenAI embeddings
            self.embeddings = OpenAIEmbeddings(
                model=config.EMBEDDING_MODEL,
                openai_api_key=config.OPENAI_API_KEY
            )
            
            # Create collection if it doesn't exist
            self._create_collection_if_not_exists()
            
            # Initialize LangChain Qdrant vector store
            self.vector_store = Qdrant(
                client=self.client,
                collection_name=config.COLLECTION_NAME,
                embeddings=self.embeddings
            )
            
            logger.info("Qdrant vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant vector store: {e}")
            raise
    
    def _create_collection_if_not_exists(self):
        """Create Qdrant collection if it doesn't exist"""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if config.COLLECTION_NAME not in collection_names:
                # Create collection with appropriate vector configuration
                self.client.create_collection(
                    collection_name=config.COLLECTION_NAME,
                    vectors_config=models.VectorParams(
                        size=1536,  # OpenAI ada-002 embedding dimension
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {config.COLLECTION_NAME}")
            else:
                logger.info(f"Collection {config.COLLECTION_NAME} already exists")
                
        except ResponseHandlingException as e:
            logger.error(f"Failed to create collection: {e}")
            raise
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store"""
        try:
            if not self.vector_store:
                raise ValueError("Vector store not initialized")
            
            # Add documents and return IDs
            ids = self.vector_store.add_documents(documents)
            logger.info(f"Added {len(documents)} documents to vector store")
            return ids
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 4,
        score_threshold: Optional[float] = None
    ) -> List[Document]:
        """Perform similarity search"""
        try:
            if not self.vector_store:
                raise ValueError("Vector store not initialized")
            
            if score_threshold:
                # Use similarity search with score threshold
                docs_and_scores = self.vector_store.similarity_search_with_score(
                    query, k=k
                )
                # Filter by score threshold
                docs = [doc for doc, score in docs_and_scores if score >= score_threshold]
            else:
                docs = self.vector_store.similarity_search(query, k=k)
            
            logger.info(f"Found {len(docs)} similar documents for query")
            return docs
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {e}")
            raise
    
    def delete_collection(self):
        """Delete the entire collection"""
        try:
            self.client.delete_collection(config.COLLECTION_NAME)
            logger.info(f"Deleted collection: {config.COLLECTION_NAME}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        try:
            info = self.client.get_collection(config.COLLECTION_NAME)
            return {
                "name": info.config.params.vectors.size,
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check if Qdrant is healthy and accessible"""
        try:
            # Try to get collections as a health check
            self.client.get_collections()
            return True
        except Exception:
            return False