#!/usr/bin/env python3
"""
Example script demonstrating RAG application usage
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_app.core.rag_chain import RAGChain
from src.rag_app.utils.logging_config import setup_logging

def main():
    """Main example function"""
    
    # Setup logging
    setup_logging(level="INFO")
    
    print("🚀 RAG Application Example")
    print("=" * 50)
    
    try:
        # Initialize RAG chain
        print("📚 Initializing RAG system...")
        rag = RAGChain()
        
        # Add sample document
        print("📄 Adding sample document...")
        sample_doc_path = Path(__file__).parent / "sample_document.txt"
        
        if sample_doc_path.exists():
            result = rag.add_documents_from_source(
                source=str(sample_doc_path),
                source_type="file"
            )
            
            if result["status"] == "success":
                print(f"✅ {result['message']}")
                stats = result.get("stats", {})
                print(f"   - Total documents: {stats.get('total_documents', 0)}")
                print(f"   - Total characters: {stats.get('total_characters', 0)}")
                print(f"   - Average chunk size: {stats.get('average_chunk_size', 0):.0f}")
            else:
                print(f"❌ Error adding document: {result['message']}")
                return
        else:
            print(f"❌ Sample document not found at {sample_doc_path}")
            return
        
        # Example queries
        queries = [
            "What is machine learning?",
            "What are the types of machine learning?",
            "How does deep learning work?",
            "What are some applications of AI in healthcare?",
            "What challenges does AI face?"
        ]
        
        print("\n🤖 Running example queries...")
        print("-" * 30)
        
        for i, query in enumerate(queries, 1):
            print(f"\n{i}. Question: {query}")
            
            result = rag.query(query, k=3)
            
            if result["status"] == "success":
                print(f"   Answer: {result['answer'][:200]}...")
                print(f"   Sources used: {result['num_sources']}")
            else:
                print(f"   Error: {result['message']}")
        
        # Conversational example
        print("\n💬 Testing conversational mode...")
        print("-" * 30)
        
        # First question
        result1 = rag.query("What is supervised learning?", use_memory=True)
        if result1["status"] == "success":
            print(f"Q1: What is supervised learning?")
            print(f"A1: {result1['answer'][:150]}...")
        
        # Follow-up question that references previous context
        result2 = rag.query("Can you give me examples of algorithms for this type?", use_memory=True)
        if result2["status"] == "success":
            print(f"\nQ2: Can you give me examples of algorithms for this type?")
            print(f"A2: {result2['answer'][:150]}...")
        
        # System status
        print("\n📊 System Status:")
        print("-" * 20)
        status = rag.get_system_status()
        print(f"Vector Store: {'✅ Healthy' if status.get('vector_store_healthy') else '❌ Unhealthy'}")
        print(f"LLM Model: {status.get('llm_model', 'Unknown')}")
        print(f"Memory Messages: {status.get('memory_messages', 0)}")
        
        print("\n🎉 Example completed successfully!")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())