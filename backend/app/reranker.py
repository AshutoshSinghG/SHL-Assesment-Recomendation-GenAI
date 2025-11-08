"""
LLM-based re-ranking for assessment recommendations.
"""

import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


class LLMReranker:
    def __init__(self, provider: str = "gemini"):
        """
        Initialize LLM reranker.
        
        Args:
            provider: "gemini" or "openai"
        """
        self.provider = provider
        
        if provider == "gemini":
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            self.genai = genai
        elif provider == "openai":
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            self.client = OpenAI(api_key=api_key)
            self.model_name = "gpt-4"
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def rerank(self, query: str, assessments: List[Dict], top_k: int = 10) -> List[Dict]:
        """
        Re-rank assessments based on relevance to the query using LLM.
        
        Args:
            query: Job description or query text
            assessments: List of assessment dictionaries
            top_k: Number of top results to return
            
        Returns:
            Re-ranked list of assessments
        """
        if not assessments:
            return []
        
        # Create prompt for reranking
        assessments_text = "\n".join([
            f"{i+1}. {assess['name']} ({assess.get('type', 'Unknown')}): {assess.get('description', 'No description')}"
            for i, assess in enumerate(assessments)
        ])
        
        prompt = f"""You are an expert in HR and talent assessment. Given a job description or query, rank the following SHL assessments by relevance and importance for that role.

Job Description/Query:
{query}

Available Assessments:
{assessments_text}

Please rank these assessments from most relevant (1) to least relevant ({len(assessments)}). 
Return only the numbers in order of relevance, separated by commas. For example: 3,1,5,2,4

Ranked order:"""

        try:
            if self.provider == "gemini":
                response = self.model.generate_content(prompt)
                ranked_text = response.text.strip()
            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are an expert in HR and talent assessment."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                ranked_text = response.choices[0].message.content.strip()
            else:
                return assessments[:top_k]
            
            # Parse the ranked order
            ranked_indices = self._parse_ranked_order(ranked_text, len(assessments))
            
            # Reorder assessments based on ranking
            reranked = [assessments[i-1] for i in ranked_indices if 1 <= i <= len(assessments)]
            
            # Add any assessments that weren't in the ranking
            ranked_set = set(ranked_indices)
            for i, assess in enumerate(assessments):
                if (i+1) not in ranked_set:
                    reranked.append(assess)
            
            return reranked[:top_k]
            
        except Exception as e:
            print(f"Error during reranking: {e}. Returning original order.")
            return assessments[:top_k]

    def _parse_ranked_order(self, text: str, max_num: int) -> List[int]:
        """
        Parse the ranked order from LLM response.
        
        Args:
            text: LLM response text
            max_num: Maximum number of assessments
            
        Returns:
            List of indices in ranked order
        """
        # Extract numbers from the text
        import re
        numbers = re.findall(r'\d+', text)
        
        ranked_indices = []
        seen = set()
        
        for num_str in numbers:
            num = int(num_str)
            if 1 <= num <= max_num and num not in seen:
                ranked_indices.append(num)
                seen.add(num)
        
        # If we didn't get enough numbers, fill in the rest
        if len(ranked_indices) < max_num:
            for i in range(1, max_num + 1):
                if i not in seen:
                    ranked_indices.append(i)
        
        return ranked_indices[:max_num]


def get_reranker(enable_reranking: bool = True) -> LLMReranker:
    """
    Get the appropriate reranker based on available API keys.
    
    Args:
        enable_reranking: Whether to enable reranking
        
    Returns:
        LLMReranker instance or None
    """
    if not enable_reranking:
        return None
    
    # Try Gemini first (better for this task)
    if os.getenv("GEMINI_API_KEY"):
        try:
            return LLMReranker("gemini")
        except Exception as e:
            print(f"Could not initialize Gemini reranker: {e}")
    
    # Try OpenAI
    if os.getenv("OPENAI_API_KEY"):
        try:
            return LLMReranker("openai")
        except Exception as e:
            print(f"Could not initialize OpenAI reranker: {e}")
    
    print("No API keys found for reranking. Reranking will be disabled.")
    return None

