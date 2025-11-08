"""
Main recommendation engine for SHL assessments.
"""

import os
import json
from typing import List, Dict
from pathlib import Path
from .embeddings import get_embedding_generator
from .vector_store import FAISSVectorStore
from .reranker import get_reranker

# Get the backend directory (parent of app directory)
BACKEND_DIR = Path(__file__).parent.parent
DATA_DIR = BACKEND_DIR / "data"


class RecommendationEngine:
    def __init__(self, catalog_path: str = None,
                 index_path: str = None,
                 metadata_path: str = None,
                 enable_reranking: bool = True):
        """
        Initialize the recommendation engine.
        
        Args:
            catalog_path: Path to catalog JSON file (default: backend/data/catalog.json)
            index_path: Path to FAISS index file (default: backend/data/catalog_embeddings.faiss)
            metadata_path: Path to assessment metadata file (default: backend/data/catalog_metadata.json)
            enable_reranking: Whether to enable LLM reranking
        """
        # Set default paths relative to backend directory
        self.catalog_path = catalog_path or str(DATA_DIR / "catalog.json")
        self.index_path = index_path or str(DATA_DIR / "catalog_embeddings.faiss")
        self.metadata_path = metadata_path or str(DATA_DIR / "catalog_metadata.json")
        self.embedding_generator = get_embedding_generator()
        self.vector_store = None
        self.reranker = get_reranker(enable_reranking) if enable_reranking else None
        self._load_or_build_index()

    def _load_or_build_index(self):
        """Load existing index or build new one from catalog."""
        self.vector_store = FAISSVectorStore()
        
        # Try to load existing index
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                self.vector_store.load(self.index_path, self.metadata_path)
                print("Loaded existing vector store")
                return
            except Exception as e:
                print(f"Error loading vector store: {e}. Rebuilding...")
        
        # Build new index from catalog
        if not os.path.exists(self.catalog_path):
            raise FileNotFoundError(f"Catalog file not found: {self.catalog_path}")
        
        with open(self.catalog_path, 'r', encoding='utf-8') as f:
            assessments = json.load(f)
        
        if not assessments:
            raise ValueError("Catalog is empty")
        
        print(f"Building vector store for {len(assessments)} assessments...")
        
        # Generate embeddings for all assessments
        texts = [
            f"{assess['name']} {assess.get('description', '')} {assess.get('type', '')}"
            for assess in assessments
        ]
        
        print("Generating embeddings...")
        try:
            embeddings = self.embedding_generator.embed_batch(texts)
        except (RuntimeError, Exception) as e:
            # If API quota exceeded, try to fall back to alternative provider
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ['quota', '429', 'insufficient_quota', 'rate_limit', 'too_many_requests']):
                print(f"API quota exceeded with current provider. Attempting fallback...")
                # Try to get fallback embedding generator
                from .embeddings import get_embedding_generator_with_fallback
                self.embedding_generator = get_embedding_generator_with_fallback(self.embedding_generator)
                print(f"Using fallback provider: {self.embedding_generator.provider if hasattr(self.embedding_generator, 'provider') else 'sentence-transformers'}")
                embeddings = self.embedding_generator.embed_batch(texts)
            else:
                raise
        
        # Get dimension from first embedding
        dimension = len(embeddings[0])
        self.vector_store = FAISSVectorStore(dimension=dimension)
        self.vector_store.add_assessments(assessments, embeddings)
        
        # Save the index
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        self.vector_store.save(self.index_path, self.metadata_path)
        print("Vector store built and saved")

    def recommend(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Get recommendations for a given query.
        
        Args:
            query: Job description or natural language query
            top_k: Number of recommendations to return
            
        Returns:
            List of recommended assessments
        """
        # Generate query embedding
        try:
            query_embedding = self.embedding_generator.embed(query)
        except (RuntimeError, Exception) as e:
            # If API quota exceeded, try to fall back to alternative provider
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ['quota', '429', 'insufficient_quota', 'rate_limit', 'too_many_requests']):
                print(f"API quota exceeded with current provider. Attempting fallback...")
                from .embeddings import get_embedding_generator_with_fallback
                self.embedding_generator = get_embedding_generator_with_fallback(self.embedding_generator)
                print(f"Using fallback provider: {self.embedding_generator.provider if hasattr(self.embedding_generator, 'provider') else 'sentence-transformers'}")
                query_embedding = self.embedding_generator.embed(query)
            else:
                raise
        
        # Search in vector store (get more results for reranking)
        search_k = top_k * 2 if self.reranker else top_k
        results = self.vector_store.search(query_embedding, top_k=search_k)
        
        # Extract assessments (ignore similarity scores for now)
        assessments = [result[0] for result in results]
        
        # Re-rank using LLM if available
        if self.reranker and len(assessments) > 1:
            assessments = self.reranker.rerank(query, assessments, top_k)
        
        # Format results
        recommendations = []
        for assess in assessments[:top_k]:
            recommendations.append({
                "assessment_name": assess.get("name", "Unknown"),
                "assessment_url": assess.get("url", ""),
                "test_type": assess.get("type", "Unknown"),
                "description": assess.get("description", "")
            })
        
        return recommendations

