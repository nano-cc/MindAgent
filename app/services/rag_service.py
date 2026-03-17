from typing import List, Optional
from chromadb import Client, Collection
from chromadb.config import Settings
import numpy as np
import hashlib

from app.config import settings
from app.database import Session


class RagService:
    """RAG service for vector search"""

    def __init__(self):
        self.chroma_client = Client(Settings(persist_directory=settings.VECTOR_DB_PATH))
        self.collections = {}

    def _get_collection(self, kb_id: str) -> Collection:
        """Get or create ChromaDB collection for knowledge base"""
        if kb_id not in self.collections:
            collection_name = f"kb_{kb_id.replace('-', '_')}"
            self.collections[kb_id] = self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        return self.collections[kb_id]

    def embed(self, text: str) -> List[float]:
        """Generate embedding for text"""
        # Placeholder: using hash-based embedding
        # TODO: Replace with actual embedding model (BGE-M3, OpenAI embeddings, etc.)
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()

        # Create a 384-dim embedding (placeholder for BGE-M3)
        base_embedding = np.zeros(384, dtype=np.float32)
        for i, byte in enumerate(hash_bytes):
            base_embedding[i % 384] = float(byte) / 255.0

        return base_embedding.tolist()

    def add_documents(self, kb_id: str, chunks: List[tuple]) -> None:
        """Add document chunks to vector store
        Args:
            kb_id: Knowledge base ID
            chunks: List of (id, text, metadata) tuples
        """
        collection = self._get_collection(kb_id)
        if not chunks:
            return

        ids = [chunk[0] for chunk in chunks]
        texts = [chunk[1] for chunk in chunks]
        metadatas = [chunk[2] for chunk in chunks]

        # Generate embeddings
        embeddings = [self.embed(text) for text in texts]

        try:
            collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")

    def similarity_search(
        self,
        kb_id: str,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[dict] = None
    ) -> List[str]:
        """Search for similar documents
        Args:
            kb_id: Knowledge base ID
            query: Search query text
            top_k: Number of results to return
            filter_metadata: Optional metadata filter
        Returns:
            List of document texts
        """
        try:
            collection = self._get_collection(kb_id)
            query_embedding = self.embed(query)

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata
            )

            if results['documents'] and len(results['documents'][0]) > 0:
                return results['documents'][0]
            return []
        except Exception as e:
            print(f"Similarity search error: {e}")
            return []

    def delete_collection(self, kb_id: str) -> None:
        """Delete collection for a knowledge base"""
        collection_name = f"kb_{kb_id.replace('-', '_')}"
        try:
            self.chroma_client.delete_collection(name=collection_name)
            if kb_id in self.collections:
                del self.collections[kb_id]
        except Exception as e:
            print(f"Error deleting collection: {e}")

    def health_check(self) -> bool:
        """Check if vector store is healthy"""
        try:
            self.chroma_client.heartbeat()
            return True
        except Exception:
            return False
