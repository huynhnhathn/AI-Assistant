#!/usr/bin/env python3
"""
Streamlit Web Interface for RAG Application
"""

import streamlit as st
import sys
from pathlib import Path
import logging

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_app.core.rag_chain import RAGChain
from src.rag_app.core.config import config
from src.rag_app.utils.logging_config import setup_logging

# Setup logging
setup_logging(level="INFO")

# Page configuration
st.set_page_config(
    page_title="RAG Application",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def initialize_rag():
    """Initialize RAG system with caching"""
    try:
        return RAGChain()
    except Exception as e:
        st.error(f"Failed to initialize RAG system: {e}")
        return None

def main():
    """Main Streamlit application"""
    
    st.title("🤖 RAG Application")
    st.markdown("**Retrieval-Augmented Generation with LangChain, Qdrant, and OpenAI**")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # System status
        if st.button("Check System Status"):
            rag = initialize_rag()
            if rag:
                status = rag.get_system_status()
                
                st.subheader("System Status")
                
                # Vector store status
                vs_healthy = status.get("vector_store_healthy", False)
                st.write(f"**Vector Store:** {'✅ Healthy' if vs_healthy else '❌ Unhealthy'}")
                
                # Models
                st.write(f"**LLM Model:** {status.get('llm_model', 'Unknown')}")
                st.write(f"**Embedding Model:** {status.get('embedding_model', 'Unknown')}")
                
                # Collection info
                collection_info = status.get("collection_info", {})
                if isinstance(collection_info, dict) and "error" not in collection_info:
                    st.write(f"**Documents:** {collection_info.get('points_count', 0)}")
                    st.write(f"**Vectors:** {collection_info.get('vectors_count', 0)}")
                
                st.write(f"**Memory Messages:** {status.get('memory_messages', 0)}")
        
        st.divider()
        
        # Query settings
        st.subheader("⚙️ Query Settings")
        num_sources = st.slider("Number of sources", min_value=1, max_value=10, value=4)
        use_memory = st.checkbox("Use conversation memory", value=True)
        score_threshold = st.slider("Similarity threshold", min_value=0.0, max_value=1.0, value=0.0, step=0.1)
        
        if score_threshold == 0.0:
            score_threshold = None
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat Interface")
        
        # Initialize session state
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "rag_system" not in st.session_state:
            st.session_state.rag_system = initialize_rag()
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Display sources if available
                if message["role"] == "assistant" and "sources" in message:
                    with st.expander("📚 Sources"):
                        for i, source in enumerate(message["sources"], 1):
                            st.write(f"**{i}. {source['file_name']}**")
                            st.write(f"Source: {source['source']}")
                            st.write(f"Preview: {source['content_preview']}")
                            st.divider()
        
        # Chat input
        if prompt := st.chat_input("Ask a question..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            if st.session_state.rag_system:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        result = st.session_state.rag_system.query(
                            question=prompt,
                            k=num_sources,
                            score_threshold=score_threshold,
                            use_memory=use_memory
                        )
                    
                    if result["status"] == "success":
                        st.markdown(result["answer"])
                        
                        # Add assistant message to chat history
                        message_data = {
                            "role": "assistant", 
                            "content": result["answer"],
                            "sources": result.get("sources", [])
                        }
                        st.session_state.messages.append(message_data)
                        
                        # Display sources
                        if result.get("sources"):
                            with st.expander("📚 Sources"):
                                for i, source in enumerate(result["sources"], 1):
                                    st.write(f"**{i}. {source['file_name']}**")
                                    st.write(f"Source: {source['source']}")
                                    st.write(f"Preview: {source['content_preview']}")
                                    st.divider()
                    else:
                        error_msg = f"Error: {result['message']}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
            else:
                error_msg = "RAG system not initialized. Please check your configuration."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        # Clear conversation button
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = []
            if st.session_state.rag_system:
                st.session_state.rag_system.clear_memory()
            st.rerun()
    
    with col2:
        st.header("📄 Document Management")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload documents",
            type=['txt', 'pdf', 'docx', 'md'],
            accept_multiple_files=True
        )
        
        if uploaded_files and st.button("📤 Process Uploaded Files"):
            if st.session_state.rag_system:
                with st.spinner("Processing documents..."):
                    # Save uploaded files temporarily and process them
                    temp_dir = Path("temp_uploads")
                    temp_dir.mkdir(exist_ok=True)
                    
                    success_count = 0
                    for uploaded_file in uploaded_files:
                        try:
                            # Save file temporarily
                            temp_file_path = temp_dir / uploaded_file.name
                            with open(temp_file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            # Process file
                            result = st.session_state.rag_system.add_documents_from_source(
                                source=str(temp_file_path),
                                source_type="file"
                            )
                            
                            if result["status"] == "success":
                                success_count += 1
                            
                            # Clean up temp file
                            temp_file_path.unlink()
                            
                        except Exception as e:
                            st.error(f"Error processing {uploaded_file.name}: {e}")
                    
                    # Clean up temp directory
                    try:
                        temp_dir.rmdir()
                    except:
                        pass
                    
                    if success_count > 0:
                        st.success(f"Successfully processed {success_count} documents!")
                    else:
                        st.error("No documents were processed successfully.")
            else:
                st.error("RAG system not initialized.")
        
        st.divider()
        
        # URL input
        st.subheader("🌐 Add from URL")
        url = st.text_input("Enter URL:")
        
        if url and st.button("📥 Process URL"):
            if st.session_state.rag_system:
                with st.spinner("Processing URL..."):
                    result = st.session_state.rag_system.add_documents_from_source(
                        source=url,
                        source_type="url"
                    )
                    
                    if result["status"] == "success":
                        st.success(result["message"])
                        
                        # Display stats
                        stats = result.get("stats", {})
                        if stats:
                            st.write(f"**Documents:** {stats.get('total_documents', 0)}")
                            st.write(f"**Characters:** {stats.get('total_characters', 0)}")
                    else:
                        st.error(result["message"])
            else:
                st.error("RAG system not initialized.")
        
        st.divider()
        
        # Directory input
        st.subheader("📁 Add from Directory")
        directory_path = st.text_input("Enter directory path:")
        
        if directory_path and st.button("📂 Process Directory"):
            if st.session_state.rag_system:
                with st.spinner("Processing directory..."):
                    result = st.session_state.rag_system.add_documents_from_source(
                        source=directory_path,
                        source_type="directory"
                    )
                    
                    if result["status"] == "success":
                        st.success(result["message"])
                        
                        # Display stats
                        stats = result.get("stats", {})
                        if stats:
                            st.write(f"**Documents:** {stats.get('total_documents', 0)}")
                            st.write(f"**Characters:** {stats.get('total_characters', 0)}")
                    else:
                        st.error(result["message"])
            else:
                st.error("RAG system not initialized.")

if __name__ == "__main__":
    main()