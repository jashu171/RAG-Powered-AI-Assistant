import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
import logging
import time
import hashlib

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, collection_name: str = "document_store", embedding_model: str = "all-MiniLM-L6-v2", persist_directory: str = "./chroma_db"):
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Use SentenceTransformer embedding function
        self.sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        
        # Create collection with embedding function
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.sentence_transformer_ef
        )
        
        # Keep track of document count for ID generation
        self.doc_count = self.collection.count()
        self.stats = {
            "documents_added": 0,
            "searches_performed": 0,
            "total_chunks": self.doc_count,
            "last_updated": time.time()
        }
        
        logger.info(f"VectorStore initialized with {self.doc_count} existing documents")
    
    def add_documents(self, chunks: List[str], metadata: Optional[Dict[str, Any]] = None):
        """Add documents to the vector store with optional metadata"""
        if not chunks:
            logger.warning("No chunks provided to add_documents")
            return
        
        try:
            # Generate unique IDs for each chunk
            ids = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                # Create unique ID based on content hash and timestamp
                chunk_hash = hashlib.md5(chunk.encode()).hexdigest()[:8]
                doc_id = f"doc_{self.doc_count + i}_{chunk_hash}"
                ids.append(doc_id)
                
                # Prepare metadata for each chunk
                chunk_metadata = {
                    "chunk_index": i,
                    "chunk_length": len(chunk),
                    "added_timestamp": time.time(),
                    "doc_id": doc_id
                }
                
                # Add provided metadata
                if metadata:
                    chunk_metadata.update(metadata)
                
                metadatas.append(chunk_metadata)
            
            # Add documents to ChromaDB collection
            self.collection.add(
                documents=chunks,
                ids=ids,
                metadatas=metadatas
            )
            
            # Update stats
            self.doc_count += len(chunks)
            self.stats["documents_added"] += 1
            self.stats["total_chunks"] += len(chunks)
            self.stats["last_updated"] = time.time()
            
            logger.info(f"Successfully added {len(chunks)} chunks to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}", exc_info=True)
            raise
    
    def search(self, query: str, k: int = 5) -> List[str]:
        """Basic search returning only document text"""
        results = self.search_with_metadata(query, k)
        return [result["document"] for result in results]
    
    def search_with_metadata(self, query: str, k: int = 5, 
                           where_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Enhanced search returning documents with metadata and scores"""
        try:
            # Check if collection is empty
            collection_count = self.collection.count()
            if collection_count == 0:
                logger.info("Vector store is empty, returning no results")
                return []
            
            # Prepare query parameters
            query_params = {
                "query_texts": [query],
                "n_results": min(k, collection_count),
                "include": ["documents", "metadatas", "distances"]
            }
            
            # Add where filter if provided
            if where_filter:
                query_params["where"] = where_filter
            
            # Query the collection
            results = self.collection.query(**query_params)
            
            # Update stats
            self.stats["searches_performed"] += 1
            
            # Process results
            if not results['documents'] or not results['documents'][0]:
                logger.info(f"No results found for query: {query}")
                return []
            
            # Combine documents, metadata, and distances
            search_results = []
            documents = results['documents'][0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]
            
            for i, doc in enumerate(documents):
                result = {
                    "document": doc,
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                    "distance": distances[i] if i < len(distances) else 1.0,
                    "similarity": 1.0 - (distances[i] if i < len(distances) else 1.0)  # Convert distance to similarity
                }
                search_results.append(result)
            
            logger.info(f"Found {len(search_results)} results for query: {query[:50]}...")
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}", exc_info=True)
            return []
    
    def search_by_file(self, query: str, file_path: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search within documents from a specific file"""
        where_filter = {"file_path": file_path}
        return self.search_with_metadata(query, k, where_filter)
    
    def get_documents_by_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Get all documents from a specific file"""
        try:
            results = self.collection.get(
                where={"file_path": file_path},
                include=["documents", "metadatas"]
            )
            
            if not results['documents']:
                return []
            
            documents_with_metadata = []
            for i, doc in enumerate(results['documents']):
                documents_with_metadata.append({
                    "document": doc,
                    "metadata": results['metadatas'][i] if i < len(results['metadatas']) else {}
                })
            
            return documents_with_metadata
            
        except Exception as e:
            logger.error(f"Error getting documents by file: {str(e)}", exc_info=True)
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the current collection"""
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "count": count,
                "embedding_model": self.embedding_model,
                "stats": self.stats.copy(),
                "last_updated": self.stats["last_updated"]
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {
                "name": self.collection_name,
                "count": 0,
                "error": str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            **self.stats,
            "current_count": self.collection.count()
        }
    
    def clear_collection(self):
        """Clear all documents from the collection"""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(name=self.collection_name)
            
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.sentence_transformer_ef
            )
            
            # Reset counters
            self.doc_count = 0
            self.stats = {
                "documents_added": 0,
                "searches_performed": 0,
                "total_chunks": 0,
                "last_updated": time.time()
            }
            
            logger.info("Vector store collection cleared successfully")
            
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}", exc_info=True)
            raise
    
    def delete_documents_by_file(self, file_path: str) -> int:
        """Delete all documents from a specific file"""
        try:
            # Get documents to delete
            docs_to_delete = self.collection.get(
                where={"file_path": file_path},
                include=["documents"]
            )
            
            if not docs_to_delete['ids']:
                logger.info(f"No documents found for file: {file_path}")
                return 0
            
            # Delete the documents
            self.collection.delete(ids=docs_to_delete['ids'])
            
            deleted_count = len(docs_to_delete['ids'])
            logger.info(f"Deleted {deleted_count} documents for file: {file_path}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting documents by file: {str(e)}", exc_info=True)
            return 0