import logging
from typing import Dict, List, Any, Optional
from .vector_service import VectorService
from .llm_service import LLMService

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, vector_service: VectorService, llm_service: LLMService):
        self.vector_service = vector_service
        self.llm_service = llm_service
        self.conversation_history = {}  # In-memory storage for conversation history
        
    async def process_query(
        self, 
        query: str, 
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process user query using RAG pipeline"""
        try:
            logger.info(f"Processing query: {query[:100]}...")
            
            # Step 1: Retrieve relevant context from vector database
            similar_docs = await self.vector_service.search_similar_documents(
                query=query,
                limit=5,
                score_threshold=0.6
            )
            
            # Extract context text
            context = [doc["content"] for doc in similar_docs]
            sources = [doc["doc_id"] for doc in similar_docs]
            
            logger.info(f"Retrieved {len(context)} relevant documents")
            
            # Step 2: Get conversation history
            conversation_history = self._get_conversation_history(conversation_id)
            
            # Step 3: Generate response using LLM
            response = await self.llm_service.generate_response(
                query=query,
                context=context,
                conversation_history=conversation_history
            )
            
            # Step 4: Update conversation history
            if conversation_id:
                self._update_conversation_history(
                    conversation_id, 
                    query, 
                    response
                )
            
            result = {
                "answer": response,
                "sources": sources,
                "context_used": len(context) > 0,
                "num_sources": len(similar_docs)
            }
            
            logger.info("Query processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise
    
    def _get_conversation_history(self, conversation_id: Optional[str]) -> List[Dict[str, str]]:
        """Get conversation history for a given conversation ID"""
        if not conversation_id:
            return []
        
        return self.conversation_history.get(conversation_id, [])
    
    def _update_conversation_history(
        self, 
        conversation_id: str, 
        user_message: str, 
        assistant_response: str
    ):
        """Update conversation history"""
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []
        
        # Add user message
        self.conversation_history[conversation_id].append({
            "role": "user",
            "content": user_message
        })
        
        # Add assistant response
        self.conversation_history[conversation_id].append({
            "role": "assistant",
            "content": assistant_response
        })
        
        # Keep only last 20 messages (10 exchanges) to manage memory
        if len(self.conversation_history[conversation_id]) > 20:
            self.conversation_history[conversation_id] = \
                self.conversation_history[conversation_id][-20:]
    
    async def add_knowledge(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Add knowledge to the vector database"""
        try:
            doc_id = await self.vector_service.add_document(
                content=content,
                metadata=metadata or {}
            )
            logger.info(f"Knowledge added with ID: {doc_id}")
            return doc_id
        except Exception as e:
            logger.error(f"Error adding knowledge: {e}")
            raise
    
    async def search_knowledge(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search knowledge base"""
        try:
            results = await self.vector_service.search_similar_documents(
                query=query,
                limit=limit,
                score_threshold=0.5
            )
            return results
        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            raise
    
    def clear_conversation_history(self, conversation_id: str) -> bool:
        """Clear conversation history for a given conversation ID"""
        try:
            if conversation_id in self.conversation_history:
                del self.conversation_history[conversation_id]
                logger.info(f"Cleared conversation history for: {conversation_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error clearing conversation history: {e}")
            return False
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get statistics about active conversations"""
        return {
            "active_conversations": len(self.conversation_history),
            "total_messages": sum(
                len(history) for history in self.conversation_history.values()
            )
        }