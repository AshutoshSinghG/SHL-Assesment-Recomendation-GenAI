# Scripts Directory

This directory contains utility scripts for the SHL Assessment Recommendation System.

## Scripts

### `crawl_catalog.py`

Web scraper for collecting SHL assessment data from the product catalog.

**Usage:**
```bash
python scripts/crawl_catalog.py
```

**Output:**
- `backend/data/catalog.json` - JSON format with all assessments
- `backend/data/catalog.csv` - CSV format with all assessments

**Features:**
- Extracts assessment names, descriptions, URLs, and types
- Handles pagination
- Includes fallback sample data
- Deduplicates assessments

### `evaluate.py`

Evaluation script to test the recommendation API with test queries and generate CSV output.

**Usage:**
```bash
# Make sure backend is running first
python scripts/evaluate.py --api-url http://localhost:8000 --output evaluation_results.csv
```

**Options:**
- `--api-url`: Backend API URL (default: http://localhost:8000)
- `--queries-file`: Path to test queries CSV (default: scripts/unlabeled_test.csv)
- `--output`: Output CSV filename (default: evaluation_results.csv)
- `--simple-output`: Simple output CSV filename (default: evaluation_results_simple.csv)
- `--top-k`: Number of recommendations per query (default: 10)

**Output:**
- Detailed CSV with all metadata
- Simplified CSV with just Query and Assessment_url

### `generate_csv.py`

Convenience wrapper around `evaluate.py` for quick CSV generation.

**Usage:**
```bash
python scripts/generate_csv.py --api-url http://localhost:8000 --output output.csv
```

### `setup.py`

Setup script to initialize the system.

**Usage:**
```bash
python scripts/setup.py
```

**What it does:**
1. Collects SHL catalog data (if not exists)
2. Checks environment variables
3. Installs backend dependencies
4. Installs frontend dependencies
5. Provides next steps

### `unlabeled_test.csv`

Test queries file with sample job descriptions for evaluation.

**Format:**
```csv
query
Hiring for Python Developer with strong problem-solving skills
Looking for a Data Analyst with SQL and Python experience
...
```

You can edit this file to add your own test queries.

