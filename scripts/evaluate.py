"""
Evaluation script to test the recommendation API with test queries.
Generates CSV output with query and assessment URLs.
"""

import requests
import csv
import json
import os
import sys
from typing import List, Dict
import time


class RecommendationEvaluator:
    def __init__(self, api_url: str = "http://localhost:8000"):
        """
        Initialize evaluator.
        
        Args:
            api_url: Base URL of the recommendation API
        """
        self.api_url = api_url.rstrip('/')
        self.results = []

    def check_api_health(self) -> bool:
        """Check if the API is running and healthy."""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"API health check failed: {e}")
            return False

    def get_recommendations(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Get recommendations for a query.
        
        Args:
            query: Job description or query text
            top_k: Number of recommendations to get
            
        Returns:
            List of recommendations
        """
        try:
            response = requests.post(
                f"{self.api_url}/recommend",
                json={"query": query, "top_k": top_k},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get("recommendations", [])
        except Exception as e:
            print(f"Error getting recommendations for query '{query}': {e}")
            return []

    def evaluate_queries(self, queries: List[str], top_k: int = 10) -> List[Dict]:
        """
        Evaluate multiple queries.
        
        Args:
            queries: List of query strings
            top_k: Number of recommendations per query
            
        Returns:
            List of evaluation results
        """
        results = []
        
        for i, query in enumerate(queries, 1):
            print(f"Processing query {i}/{len(queries)}: {query[:50]}...")
            
            recommendations = self.get_recommendations(query, top_k)
            
            # Create result rows (one per recommendation)
            for rec in recommendations:
                results.append({
                    "query": query,
                    "assessment_name": rec.get("assessment_name", ""),
                    "assessment_url": rec.get("assessment_url", ""),
                    "test_type": rec.get("test_type", ""),
                    "rank": recommendations.index(rec) + 1
                })
            
            # Add spacing between queries in results
            if recommendations:
                results.append({
                    "query": "",
                    "assessment_name": "",
                    "assessment_url": "",
                    "test_type": "",
                    "rank": ""
                })
            
            time.sleep(0.5)  # Be polite to the API
        
        self.results = results
        return results

    def save_to_csv(self, filename: str = "evaluation_results.csv"):
        """
        Save results to CSV file.
        
        Args:
            filename: Output CSV filename
        """
        if not self.results:
            print("No results to save")
            return
        
        # Filter out empty rows for the final output
        filtered_results = [r for r in self.results if r.get("query")]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["query", "assessment_url", "assessment_name", "test_type", "rank"]
            )
            writer.writeheader()
            writer.writerows(filtered_results)
        
        print(f"Saved {len(filtered_results)} results to {filename}")

    def save_simple_csv(self, filename: str = "evaluation_results_simple.csv"):
        """
        Save simplified CSV with only query and assessment_url (as per requirements).
        
        Args:
            filename: Output CSV filename
        """
        if not self.results:
            print("No results to save")
            return
        
        # Filter out empty rows and create simplified format
        filtered_results = []
        for r in self.results:
            if r.get("query") and r.get("assessment_url"):
                filtered_results.append({
                    "Query": r["query"],
                    "Assessment_url": r["assessment_url"]
                })
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Query", "Assessment_url"])
            writer.writeheader()
            writer.writerows(filtered_results)
        
        print(f"Saved {len(filtered_results)} simplified results to {filename}")


def load_test_queries(filepath: str = "scripts/unlabeled_test.csv") -> List[str]:
    """
    Load test queries from a CSV file.
    
    Args:
        filepath: Path to CSV file with test queries
        
    Returns:
        List of query strings
    """
    queries = []
    
    if not os.path.exists(filepath):
        print(f"Test queries file not found: {filepath}")
        print("Using default test queries...")
        return get_default_test_queries()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Try different column names
                query = row.get("query") or row.get("Query") or row.get("text") or row.get("job_description")
                if query:
                    queries.append(query.strip())
    except Exception as e:
        print(f"Error loading test queries: {e}")
        return get_default_test_queries()
    
    return queries if queries else get_default_test_queries()


def get_default_test_queries() -> List[str]:
    """Get default test queries if file is not found."""
    return [
        "Hiring for Python Developer with strong problem-solving skills",
        "Looking for a Data Analyst with SQL and Python experience",
        "Seeking a Customer Service Representative with excellent communication skills",
        "Need a Project Manager with leadership and organizational abilities",
        "Hiring for a Software Engineer with Java and Spring Boot experience",
        "Looking for a Sales Manager with negotiation and relationship-building skills",
        "Seeking a UX Designer with creative thinking and user research experience",
        "Need a Financial Analyst with numerical reasoning and analytical skills",
        "Hiring for a Marketing Manager with strategic thinking and communication skills",
        "Looking for a DevOps Engineer with cloud infrastructure and automation experience"
    ]


def main():
    """Main evaluation function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate SHL Recommendation API")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--queries-file", default="scripts/unlabeled_test.csv", help="Path to test queries CSV")
    parser.add_argument("--output", default="evaluation_results.csv", help="Output CSV filename")
    parser.add_argument("--simple-output", default="evaluation_results_simple.csv", help="Simple output CSV filename")
    parser.add_argument("--top-k", type=int, default=10, help="Number of recommendations per query")
    
    args = parser.parse_args()
    
    # Initialize evaluator
    evaluator = RecommendationEvaluator(api_url=args.api_url)
    
    # Check API health
    print(f"Checking API health at {args.api_url}...")
    if not evaluator.check_api_health():
        print("ERROR: API is not available. Please make sure the backend server is running.")
        sys.exit(1)
    
    print("API is healthy!\n")
    
    # Load test queries
    print(f"Loading test queries from {args.queries_file}...")
    queries = load_test_queries(args.queries_file)
    print(f"Loaded {len(queries)} test queries\n")
    
    # Evaluate queries
    print("Starting evaluation...")
    evaluator.evaluate_queries(queries, top_k=args.top_k)
    
    # Save results
    print("\nSaving results...")
    evaluator.save_to_csv(args.output)
    evaluator.save_simple_csv(args.simple_output)
    
    print("\nEvaluation complete!")


if __name__ == "__main__":
    main()

