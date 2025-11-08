"""
Vector store implementation using FAISS for similarity search.
"""

import json
import os
import pickle
from typing import List, Dict, Tuple
import numpy as np
import faiss


class FAISSVectorStore:
    def __init__(self, dimension: int = 384):
        """
        Initialize FAISS vector store.
        
        Args:
            dimension: Dimension of the embeddings
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.assessments = []
        self.embeddings_array = None

    def add_assessments(self, assessments: List[Dict], embeddings: List[List[float]]):
        """
        Add assessments and their embeddings to the vector store.
        
        Args:
            assessments: List of assessment dictionaries
            embeddings: List of embedding vectors
        """
        if len(assessments) != len(embeddings):
            raise ValueError("Number of assessments must match number of embeddings")
        
        self.assessments = assessments
        self.embeddings_array = np.array(embeddings, dtype='float32')
        
        # Clear existing index and add all embeddings
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(self.embeddings_array)
        print(f"Added {len(assessments)} assessments to vector store")

    def search(self, query_embedding: List[float], top_k: int = 10) -> List[Tuple[Dict, float]]:
        """
        Search for similar assessments.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of tuples (assessment_dict, similarity_score)
        """
        if self.index.ntotal == 0:
            return []
        
        query_vector = np.array([query_embedding], dtype='float32')
        
        # Search in FAISS
        distances, indices = self.index.search(query_vector, min(top_k, len(self.assessments)))
        
        # Return results with assessments and distances
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.assessments):
                results.append((self.assessments[idx], float(distance)))
        
        return results

    def save(self, index_path: str, metadata_path: str):
        """
        Save the vector store to disk.
        
        Args:
            index_path: Path to save FAISS index
            metadata_path: Path to save assessment metadata
        """
        faiss.write_index(self.index, index_path)
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.assessments, f, indent=2, ensure_ascii=False)
        print(f"Saved vector store to {index_path} and {metadata_path}")

    def load(self, index_path: str, metadata_path: str):
        """
        Load the vector store from disk.
        
        Args:
            index_path: Path to load FAISS index from
            metadata_path: Path to load assessment metadata from
        """
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            self.index = faiss.read_index(index_path)
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.assessments = json.load(f)
            # Reconstruct embeddings array dimension from first assessment if needed
            if self.assessments and self.index.ntotal > 0:
                self.dimension = self.index.d
            print(f"Loaded vector store with {len(self.assessments)} assessments")
        else:
            print(f"Vector store files not found at {index_path} or {metadata_path}")

