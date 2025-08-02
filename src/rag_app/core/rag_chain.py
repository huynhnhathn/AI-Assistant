import logging
from typing import List, Dict, Any, Optional, Tuple
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory

from .config import config
from .vector_store import QdrantVectorStore
from .document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

class RAGChain:
    """RAG (Retrieval-Augmented Generation) chain implementation"""
    
    def __init__(self):
        self.vector_store = None
        self.document_processor = None
        self.llm = None
        self.memory = None
        self.qa_chain = None
        self._initialize()
    
    def _initialize(self):
        """Initialize RAG components"""
        try:
            # Initialize vector store
            self.vector_store = QdrantVectorStore()
            
            # Initialize document processor
            self.document_processor = DocumentProcessor()
            
            # Initialize OpenAI LLM
            self.llm = ChatOpenAI(
                model=config.LLM_MODEL,
                temperature=config.TEMPERATURE,
                max_tokens=config.MAX_TOKENS,
                openai_api_key=config.OPENAI_API_KEY
            )
            
            # Initialize conversation memory
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            logger.info("RAG chain initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG chain: {e}")
            raise
    
    def add_documents_from_source(
        self, 
        source: str, 
        source_type: str = "file",
        glob_pattern: str = "**/*"
    ) -> Dict[str, Any]:
        """Add documents to the vector store from various sources"""
        try:
            # Process documents
            documents = self.document_processor.process_documents(
                source=source,
                source_type=source_type,
                glob_pattern=glob_pattern
            )
            
            if not documents:
                return {"status": "error", "message": "No documents found or processed"}
            
            # Add to vector store
            ids = self.vector_store.add_documents(documents)
            
            # Get document statistics
            stats = self.document_processor.get_document_stats(documents)
            
            result = {
                "status": "success",
                "message": f"Successfully added {len(documents)} document chunks",
                "document_ids": ids,
                "stats": stats
            }
            
            logger.info(f"Added {len(documents)} documents from {source}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to add documents from {source}: {e}")
            return {"status": "error", "message": str(e)}
    
    def _create_qa_prompt(self) -> ChatPromptTemplate:
        """Create the QA prompt template"""
        template = """You are a helpful AI assistant that answers questions based on the provided context. 
        Use the following pieces of context to answer the question at the end. 
        If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.

        Context:
        {context}

        Question: {question}

        Please provide a comprehensive and accurate answer based on the context provided."""
        
        return ChatPromptTemplate.from_template(template)
    
    def _create_conversational_prompt(self) -> ChatPromptTemplate:
        """Create a conversational prompt template with memory"""
        template = """You are a helpful AI assistant that answers questions based on the provided context and conversation history.
        Use the following pieces of context to answer the question at the end.
        Also consider the conversation history to provide more relevant and contextual responses.
        If you don't know the answer based on the context, just say that you don't know.

        Context:
        {context}

        Conversation History:
        {chat_history}

        Current Question: {question}

        Answer:"""
        
        return ChatPromptTemplate.from_template(template)
    
    def query(
        self, 
        question: str, 
        k: int = 4,
        score_threshold: Optional[float] = None,
        use_memory: bool = False
    ) -> Dict[str, Any]:
        """Query the RAG system"""
        try:
            if not self.vector_store.vector_store:
                return {
                    "status": "error",
                    "message": "Vector store not initialized. Please add documents first."
                }
            
            # Retrieve relevant documents
            relevant_docs = self.vector_store.similarity_search(
                query=question,
                k=k,
                score_threshold=score_threshold
            )
            
            if not relevant_docs:
                return {
                    "status": "success",
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": [],
                    "context_used": []
                }
            
            # Prepare context
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            # Create prompt
            if use_memory:
                prompt = self._create_conversational_prompt()
                chat_history = self.memory.chat_memory.messages
                chat_history_str = "\n".join([
                    f"Human: {msg.content}" if msg.type == "human" else f"Assistant: {msg.content}"
                    for msg in chat_history[-6:]  # Last 3 exchanges
                ])
                
                # Create chain
                chain = (
                    {
                        "context": lambda x: context,
                        "question": RunnablePassthrough(),
                        "chat_history": lambda x: chat_history_str
                    }
                    | prompt
                    | self.llm
                    | StrOutputParser()
                )
            else:
                prompt = self._create_qa_prompt()
                chain = (
                    {
                        "context": lambda x: context,
                        "question": RunnablePassthrough()
                    }
                    | prompt
                    | self.llm
                    | StrOutputParser()
                )
            
            # Generate answer
            answer = chain.invoke(question)
            
            # Update memory if using conversational mode
            if use_memory:
                self.memory.chat_memory.add_user_message(question)
                self.memory.chat_memory.add_ai_message(answer)
            
            # Prepare sources
            sources = []
            for doc in relevant_docs:
                source_info = {
                    "source": doc.metadata.get("source", "Unknown"),
                    "file_name": doc.metadata.get("file_name", "Unknown"),
                    "chunk_id": doc.metadata.get("chunk_id", 0),
                    "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                }
                sources.append(source_info)
            
            result = {
                "status": "success",
                "answer": answer,
                "sources": sources,
                "context_used": [doc.page_content for doc in relevant_docs],
                "num_sources": len(relevant_docs)
            }
            
            logger.info(f"Successfully answered query with {len(relevant_docs)} sources")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process query: {e}")
            return {"status": "error", "message": str(e)}
    
    def batch_query(self, questions: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Process multiple queries"""
        try:
            results = []
            for question in questions:
                result = self.query(question, **kwargs)
                results.append(result)
            
            logger.info(f"Processed {len(questions)} batch queries")
            return results
            
        except Exception as e:
            logger.error(f"Failed to process batch queries: {e}")
            return [{"status": "error", "message": str(e)} for _ in questions]
    
    def clear_memory(self):
        """Clear conversation memory"""
        try:
            self.memory.clear()
            logger.info("Conversation memory cleared")
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        try:
            messages = self.memory.chat_memory.messages
            history = []
            
            for msg in messages:
                history.append({
                    "type": "human" if msg.type == "human" else "assistant",
                    "content": msg.content
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and health"""
        try:
            # Check vector store health
            vector_store_healthy = self.vector_store.health_check()
            
            # Get collection info
            collection_info = None
            if vector_store_healthy:
                try:
                    collection_info = self.vector_store.get_collection_info()
                except Exception:
                    collection_info = {"error": "Could not retrieve collection info"}
            
            status = {
                "vector_store_healthy": vector_store_healthy,
                "llm_model": config.LLM_MODEL,
                "embedding_model": config.EMBEDDING_MODEL,
                "collection_info": collection_info,
                "memory_messages": len(self.memory.chat_memory.messages) if self.memory else 0
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {"error": str(e)}