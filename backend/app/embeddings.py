"""
Embedding generation and management for SHL assessments.
Supports OpenAI and Google Gemini embeddings.
"""

import os
from typing import List, Optional
import numpy as np
from dotenv import load_dotenv

load_dotenv()


class EmbeddingGenerator:
    def __init__(self, provider: str = "openai"):
        """
        Initialize embedding generator.
        
        Args:
            provider: "openai" or "gemini"
        """
        self.provider = provider
        
        if provider == "openai":
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            self.client = OpenAI(api_key=api_key)
            self.model = "text-embedding-3-small"
        elif provider == "gemini":
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            genai.configure(api_key=api_key)
            self.genai = genai
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of embedding values
            
        Raises:
            Exception: If embedding generation fails (e.g., quota exceeded)
        """
        if self.provider == "openai":
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                error_msg = str(e).lower()
                # Check for quota/rate limit errors
                if any(keyword in error_msg for keyword in ['quota', '429', 'insufficient_quota', 'rate_limit', 'too_many_requests']):
                    raise RuntimeError(f"OpenAI API quota exceeded. Error: {e}. Please use Gemini API or sentence-transformers fallback.")
                # Re-raise other exceptions
                raise
        elif self.provider == "gemini":
            try:
                # Gemini embeddings (using text-embedding-004)
                result = self.genai.embed_content(
                    model="models/text-embedding-004",
                    content=text,
                    task_type="retrieval_document"
                )
                return result['embedding']
            except Exception as e:
                error_msg = str(e).lower()
                if 'quota' in error_msg or '429' in error_msg:
                    raise RuntimeError(f"Gemini API quota exceeded. Error: {e}. Please use sentence-transformers fallback.")
                raise
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            batch_size: Number of texts to process in each batch
            
        Returns:
            List of embeddings
            
        Raises:
            Exception: If embedding generation fails (e.g., quota exceeded)
        """
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                if self.provider == "openai":
                    response = self.client.embeddings.create(
                        model=self.model,
                        input=batch
                    )
                    batch_embeddings = [item.embedding for item in response.data]
                elif self.provider == "gemini":
                    batch_embeddings = []
                    for text in batch:
                        result = self.genai.embed_content(
                            model="models/text-embedding-004",
                            content=text,
                            task_type="retrieval_document"
                        )
                        batch_embeddings.append(result['embedding'])
                else:
                    raise ValueError(f"Unsupported provider: {self.provider}")
                
                embeddings.extend(batch_embeddings)
            except Exception as e:
                error_msg = str(e).lower()
                # Check for quota/rate limit errors
                if any(keyword in error_msg for keyword in ['quota', '429', 'insufficient_quota', 'rate_limit', 'too_many_requests']):
                    if self.provider == "openai":
                        raise RuntimeError(f"OpenAI API quota exceeded. Error: {e}. Please use Gemini API or sentence-transformers fallback.")
                    elif self.provider == "gemini":
                        raise RuntimeError(f"Gemini API quota exceeded. Error: {e}. Please use sentence-transformers fallback.")
                # Re-raise other exceptions
                raise
        
        return embeddings


class FallbackEmbeddingGenerator:
    """
    Fallback to sentence-transformers if API keys are not available.
    """
    def __init__(self):
        try:
            from sentence_transformers import SentenceTransformer
            print("Loading sentence-transformers model 'all-MiniLM-L6-v2'...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.available = True
            self.provider = "sentence-transformers"
            print("Fallback embedding model loaded successfully")
        except Exception as e:
            print(f"Warning: Could not load sentence-transformers: {e}")
            print("Please install sentence-transformers: pip install sentence-transformers")
            self.available = False
            self.model = None
            self.provider = None

    def embed(self, text: str) -> List[float]:
        if not self.available:
            raise RuntimeError("Fallback embedding model not available. Please install sentence-transformers or provide an API key.")
        return self.model.encode(text).tolist()

    def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        if not self.available:
            raise RuntimeError("Fallback embedding model not available. Please install sentence-transformers or provide an API key.")
        embeddings = self.model.encode(texts, batch_size=batch_size, show_progress_bar=False)
        return embeddings.tolist()


def get_embedding_generator():
    """
    Get the appropriate embedding generator based on available API keys.
    Returns EmbeddingGenerator or FallbackEmbeddingGenerator.
    """
    # Try OpenAI first
    if os.getenv("OPENAI_API_KEY"):
        try:
            return EmbeddingGenerator("openai")
        except Exception as e:
            print(f"Could not initialize OpenAI embeddings: {e}")
    
    # Try Gemini
    if os.getenv("GEMINI_API_KEY"):
        try:
            return EmbeddingGenerator("gemini")
        except Exception as e:
            print(f"Could not initialize Gemini embeddings: {e}")
    
    # Fallback to sentence-transformers
    print("No API keys found. Using local sentence-transformers model...")
    return FallbackEmbeddingGenerator()


def get_embedding_generator_with_fallback(current_generator):
    """
    Get a fallback embedding generator when the current one fails (e.g., quota exceeded).
    
    Args:
        current_generator: The current embedding generator that failed
        
    Returns:
        A fallback embedding generator (Gemini -> sentence-transformers, or OpenAI -> Gemini -> sentence-transformers)
    """
    # If current is OpenAI, try Gemini
    if hasattr(current_generator, 'provider') and current_generator.provider == "openai":
        if os.getenv("GEMINI_API_KEY"):
            try:
                print("Falling back to Gemini embeddings...")
                return EmbeddingGenerator("gemini")
            except Exception as e:
                print(f"Could not initialize Gemini embeddings: {e}")
    
    # If current is Gemini or OpenAI failed, use sentence-transformers
    print("Falling back to sentence-transformers (local model)...")
    return FallbackEmbeddingGenerator()

