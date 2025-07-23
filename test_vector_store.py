#!/usr/bin/env python3
"""
Test Vector Store Document Processing

This script tests document processing and storage in the vector database.
"""

import os
from dotenv import load_dotenv
from utils.document_parser import DocumentParser
from utils.vector_store import VectorStore
import chromadb

def test_vector_store_processing():
    """Test document processing and storage in vector database"""
    print("🧪 Testing Vector Store Document Processing")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Initialize vector store
    vector_store = VectorStore()
    
    # Check if collection exists and is empty
    collection_info = vector_store.get_collection_info()
    print(f"✅ Collection exists: {vector_store.collection is not None}")
    print(f"✅ Collection info: {collection_info}")
    print(f"✅ Document count before: {vector_store.collection.count()}")
    
    # Process a test document from uploads folder
    uploads_dir = "uploads"
    test_files = os.listdir(uploads_dir)
    pdf_files = [f for f in test_files if f.endswith(".pdf")]
    
    if not pdf_files:
        print("❌ No PDF files found in uploads folder")
        return False
    
    test_file = os.path.join(uploads_dir, pdf_files[0])
    print(f"\n📄 Processing test file: {test_file}")
    
    # Parse document into chunks
    parser = DocumentParser()
    chunks = parser.parse_file(test_file)
    
    if not chunks:
        print(f"❌ Failed to parse {test_file} into chunks")
        return False
    
    print(f"✅ Document parsed into {len(chunks)} chunks")
    
    # Add chunks to vector store
    print("\n🔄 Adding chunks to vector store...")
    
    for i, chunk in enumerate(chunks):
        vector_store.add_documents(
            chunks=[chunk],
            metadata={
                "file_path": test_file,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
        )
    
    # Verify documents were added
    updated_count = vector_store.collection.count()
    print(f"✅ Document count after: {updated_count}")
    
    # Test retrieval
    if updated_count > 0:
        print("\n🔍 Testing retrieval...")
        results = vector_store.search(
            query="resume",
            k=2
        )
        
        print(f"✅ Search results: {len(results)} chunks found")
        if results:
            print(f"Sample content: {results[0][:100]}...")
        
        # Get all documents for the file
        file_docs = vector_store.get_documents_by_file(test_file)
        print(f"✅ File documents: {len(file_docs)} chunks found")
    
    print("\n🎉 Vector store test completed!")
    return True

def main():
    """Run the test"""
    test_vector_store_processing()

if __name__ == "__main__":
    main()