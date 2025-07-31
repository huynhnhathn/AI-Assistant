import logging
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    DirectoryLoader,
    WebBaseLoader
)

from .config import config

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Document processing for loading and chunking various document types"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Supported file extensions and their loaders
        self.loader_mapping = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.txt': TextLoader,
            '.md': TextLoader,
            '.py': TextLoader,
            '.js': TextLoader,
            '.html': TextLoader,
            '.json': TextLoader,
            '.csv': TextLoader
        }
    
    def load_document(self, file_path: str) -> List[Document]:
        """Load a single document"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            extension = file_path.suffix.lower()
            
            if extension not in self.loader_mapping:
                raise ValueError(f"Unsupported file type: {extension}")
            
            # Get appropriate loader
            loader_class = self.loader_mapping[extension]
            loader = loader_class(str(file_path))
            
            # Load document
            documents = loader.load()
            
            # Add metadata
            for doc in documents:
                doc.metadata.update({
                    'source': str(file_path),
                    'file_type': extension,
                    'file_name': file_path.name
                })
            
            logger.info(f"Loaded {len(documents)} documents from {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to load document {file_path}: {e}")
            raise
    
    def load_directory(self, directory_path: str, glob_pattern: str = "**/*") -> List[Document]:
        """Load all supported documents from a directory"""
        try:
            directory_path = Path(directory_path)
            
            if not directory_path.exists():
                raise FileNotFoundError(f"Directory not found: {directory_path}")
            
            all_documents = []
            
            # Get all files matching the pattern
            files = list(directory_path.glob(glob_pattern))
            
            for file_path in files:
                if file_path.is_file() and file_path.suffix.lower() in self.loader_mapping:
                    try:
                        documents = self.load_document(str(file_path))
                        all_documents.extend(documents)
                    except Exception as e:
                        logger.warning(f"Failed to load {file_path}: {e}")
                        continue
            
            logger.info(f"Loaded {len(all_documents)} documents from directory {directory_path}")
            return all_documents
            
        except Exception as e:
            logger.error(f"Failed to load directory {directory_path}: {e}")
            raise
    
    def load_from_urls(self, urls: List[str]) -> List[Document]:
        """Load documents from web URLs"""
        try:
            all_documents = []
            
            for url in urls:
                try:
                    loader = WebBaseLoader(url)
                    documents = loader.load()
                    
                    # Add metadata
                    for doc in documents:
                        doc.metadata.update({
                            'source': url,
                            'file_type': 'web',
                            'url': url
                        })
                    
                    all_documents.extend(documents)
                    logger.info(f"Loaded {len(documents)} documents from {url}")
                    
                except Exception as e:
                    logger.warning(f"Failed to load URL {url}: {e}")
                    continue
            
            logger.info(f"Loaded {len(all_documents)} documents from {len(urls)} URLs")
            return all_documents
            
        except Exception as e:
            logger.error(f"Failed to load URLs: {e}")
            raise
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        try:
            chunked_documents = []
            
            for doc in documents:
                # Split the document
                chunks = self.text_splitter.split_documents([doc])
                
                # Add chunk metadata
                for i, chunk in enumerate(chunks):
                    chunk.metadata.update({
                        'chunk_id': i,
                        'total_chunks': len(chunks),
                        'chunk_size': len(chunk.page_content)
                    })
                
                chunked_documents.extend(chunks)
            
            logger.info(f"Split {len(documents)} documents into {len(chunked_documents)} chunks")
            return chunked_documents
            
        except Exception as e:
            logger.error(f"Failed to chunk documents: {e}")
            raise
    
    def process_documents(
        self, 
        source: str, 
        source_type: str = "file",
        glob_pattern: str = "**/*"
    ) -> List[Document]:
        """
        Process documents from various sources
        
        Args:
            source: File path, directory path, or URL(s)
            source_type: 'file', 'directory', or 'url'
            glob_pattern: Pattern for directory loading
        
        Returns:
            List of processed and chunked documents
        """
        try:
            documents = []
            
            if source_type == "file":
                documents = self.load_document(source)
            elif source_type == "directory":
                documents = self.load_directory(source, glob_pattern)
            elif source_type == "url":
                urls = [source] if isinstance(source, str) else source
                documents = self.load_from_urls(urls)
            else:
                raise ValueError(f"Unsupported source type: {source_type}")
            
            # Chunk the documents
            chunked_documents = self.chunk_documents(documents)
            
            logger.info(f"Processed {len(documents)} documents into {len(chunked_documents)} chunks")
            return chunked_documents
            
        except Exception as e:
            logger.error(f"Failed to process documents: {e}")
            raise
    
    def get_document_stats(self, documents: List[Document]) -> Dict[str, Any]:
        """Get statistics about the documents"""
        try:
            if not documents:
                return {"total_documents": 0}
            
            total_chars = sum(len(doc.page_content) for doc in documents)
            file_types = {}
            sources = set()
            
            for doc in documents:
                # Count file types
                file_type = doc.metadata.get('file_type', 'unknown')
                file_types[file_type] = file_types.get(file_type, 0) + 1
                
                # Collect sources
                source = doc.metadata.get('source', 'unknown')
                sources.add(source)
            
            return {
                "total_documents": len(documents),
                "total_characters": total_chars,
                "average_chunk_size": total_chars / len(documents),
                "file_types": file_types,
                "unique_sources": len(sources),
                "sources": list(sources)
            }
            
        except Exception as e:
            logger.error(f"Failed to get document stats: {e}")
            return {"error": str(e)}