#!/usr/bin/env python3

import json
import asyncio
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.vector_service import VectorService

async def load_sample_data():
    """Load sample documents into the vector database"""
    try:
        # Initialize vector service
        vector_service = VectorService()
        await vector_service.initialize()
        
        # Load sample documents
        with open('../data/sample_documents.json', 'r') as f:
            documents = json.load(f)
        
        print(f"Loading {len(documents)} sample documents...")
        
        # Add each document to the vector database
        for i, doc in enumerate(documents, 1):
            doc_id = await vector_service.add_document(
                content=doc['content'],
                metadata=doc['metadata']
            )
            print(f"Added document {i}/{len(documents)}: {doc['metadata']['title']} (ID: {doc_id})")
        
        # Get document count to verify
        count = await vector_service.get_document_count()
        print(f"\nTotal documents in database: {count}")
        
        print("Sample data loaded successfully!")
        
    except Exception as e:
        print(f"Error loading sample data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(load_sample_data())