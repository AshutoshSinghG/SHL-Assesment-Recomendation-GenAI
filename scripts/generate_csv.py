"""
Script to generate CSV output for given test queries.
This is a convenience wrapper around evaluate.py
"""

import sys
import os

# Add parent directory to path to import evaluate
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.evaluate import RecommendationEvaluator, load_test_queries


def main():
    """Generate CSV output for test queries."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate CSV output for test queries")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--queries-file", default="scripts/unlabeled_test.csv", help="Path to test queries CSV")
    parser.add_argument("--output", default="output.csv", help="Output CSV filename")
    
    args = parser.parse_args()
    
    # Initialize evaluator
    evaluator = RecommendationEvaluator(api_url=args.api_url)
    
    # Check API health
    if not evaluator.check_api_health():
        print("ERROR: API is not available. Please make sure the backend server is running.")
        sys.exit(1)
    
    # Load test queries
    queries = load_test_queries(args.queries_file)
    print(f"Processing {len(queries)} queries...")
    
    # Evaluate queries
    evaluator.evaluate_queries(queries, top_k=10)
    
    # Save simplified CSV (query, assessment_url)
    evaluator.save_simple_csv(args.output)
    
    print(f"CSV output saved to {args.output}")


if __name__ == "__main__":
    main()

