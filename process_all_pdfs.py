#!/usr/bin/env python3
"""
Process all PDF files in the uploads directory and store them in the vector database.
"""

import os
from utils.document_parser import DocumentParser
from utils.vector_store import VectorStore

def process_all_pdfs():
    """Process all PDF files in the uploads directory"""
    print("🧪 Processing all PDF files in uploads directory")
    print("=" * 50)
    
    # Initialize parser and vector store
    parser = DocumentParser()
    vs = VectorStore()
    
    # Get all PDF files in uploads directory
    uploads_dir = "uploads"
    pdf_files = [f for f in os.listdir(uploads_dir) if f.endswith(".pdf")]
    
    print(f"Found {len(pdf_files)} PDF files in {uploads_dir}:")
    
    # Process each PDF file
    for pdf_file in pdf_files:
        print(f"\n- {pdf_file}")
        file_path = os.path.join(uploads_dir, pdf_file)
        
        # Check if file is already in vector store
        file_docs = vs.get_documents_by_file(file_path)
        
        if not file_docs:
            print(f"  Processing {file_path}...")
            
            # Parse file into chunks
            chunks = parser.parse_file(file_path)
            
            if chunks:
                print(f"  Parsed into {len(chunks)} chunks")
                
                # Add chunks to vector store
                for i, chunk in enumerate(chunks):
                    vs.add_documents(
                        chunks=[chunk],
                        metadata={
                            "file_path": file_path,
                            "chunk_index": i,
                            "total_chunks": len(chunks)
                        }
                    )
                
                print(f"  Added to vector store")
            else:
                print(f"  Failed to parse file")
        else:
            print(f"  Already in vector store ({len(file_docs)} chunks)")
    
    # Verify documents in vector store
    collection_info = vs.get_collection_info()
    print(f"\n✅ Total documents in vector store: {collection_info['count']}")
    
    print("\n🎉 Processing completed!")
    return True

def main():
    """Run the process"""
    process_all_pdfs()

if __name__ == "__main__":
    main()