"""
Setup script to initialize the SHL Recommendation System.
Runs data collection and builds the vector store.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_command(cmd, cwd=None):
    """Run a shell command and print output."""
    print(f"\n{'='*60}")
    print(f"Running: {cmd}")
    print(f"{'='*60}\n")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=False)
    if result.returncode != 0:
        print(f"Error: Command failed with exit code {result.returncode}")
        return False
    return True

def main():
    """Main setup function."""
    print("SHL Assessment Recommendation System - Setup")
    print("=" * 60)
    
    # Step 1: Check if catalog data exists
    catalog_path = Path("backend/data/catalog.json")
    if not catalog_path.exists():
        print("\nStep 1: Collecting SHL catalog data...")
        if not run_command("python scripts/crawl_catalog.py", cwd=Path(__file__).parent.parent):
            print("Warning: Catalog scraping may have failed. Using sample data...")
    else:
        print(f"\nStep 1: Catalog data already exists at {catalog_path}")
    
    # Step 2: Check environment variables
    print("\nStep 2: Checking environment variables...")
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    
    if not has_openai and not has_gemini:
        print("WARNING: No API keys found!")
        print("Set OPENAI_API_KEY or GEMINI_API_KEY in your environment.")
        print("The system will use a local fallback model (sentence-transformers).")
        print("This may have lower quality but will work for testing.")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    else:
        if has_openai:
            print("✓ OPENAI_API_KEY found")
        if has_gemini:
            print("✓ GEMINI_API_KEY found")
    
    # Step 3: Install backend dependencies
    print("\nStep 3: Installing backend dependencies...")
    if not run_command("pip install -r backend/requirements.txt"):
        print("Error: Failed to install backend dependencies")
        return
    
    # Step 4: Install frontend dependencies
    print("\nStep 4: Installing frontend dependencies...")
    if not run_command("npm install", cwd=Path(__file__).parent.parent / "frontend"):
        print("Error: Failed to install frontend dependencies")
        return
    
    # Step 5: Build vector store (will be done on first API call, but we can trigger it)
    print("\nStep 5: Vector store will be built automatically on first API call")
    print("        (or you can start the backend server now)")
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Make sure your .env file is configured with API keys")
    print("2. Start the backend: cd backend && python main.py")
    print("3. Start the frontend: cd frontend && npm run dev")
    print("4. Open http://localhost:3000 in your browser")
    print("\nFor evaluation, run: python scripts/evaluate.py")

if __name__ == "__main__":
    main()

