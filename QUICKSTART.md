# Quick Start Guide

Get the SHL Assessment Recommendation System up and running in 5 minutes.

## Prerequisites

- Python 3.8+ installed
- Node.js 16+ installed
- API key for OpenAI or Google Gemini (optional, fallback available)

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd SHL-GenAI

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

## Step 2: Configure Environment Variables

### Backend

Create `backend/.env`:

```env
OPENAI_API_KEY=your_key_here
# OR
GEMINI_API_KEY=your_key_here

ENABLE_RERANKING=true
```

**Note:** If you don't have API keys, the system will use a local fallback model. Install it with:
```bash
pip install sentence-transformers
```

### Frontend

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

## Step 3: Collect Data (Optional)

The system includes sample data, but you can scrape fresh data:

```bash
cd scripts
python crawl_catalog.py
```

This creates `backend/data/catalog.json` with assessment data.

## Step 4: Start the Backend

```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

**First run:** The system will automatically build the vector store from the catalog data. This may take a few minutes.

## Step 5: Start the Frontend

Open a new terminal:

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Step 6: Test the System

1. Open `http://localhost:3000` in your browser
2. Enter a job description, e.g., "Hiring for Python Developer with strong problem-solving skills"
3. Click "Get Recommendations"
4. View the recommended SHL assessments

## Testing the API Directly

```bash
# Health check
curl http://localhost:8000/health

# Get recommendations
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "Python Developer", "top_k": 5}'
```

## Generate Evaluation CSV

```bash
# Make sure backend is running
cd scripts
python evaluate.py --output evaluation_results.csv
```

## Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify Python dependencies are installed
- Check `.env` file exists and has valid API keys (or install sentence-transformers)

### Frontend can't connect to backend
- Verify backend is running on port 8000
- Check `VITE_API_URL` in `frontend/.env`
- Check browser console for CORS errors

### No recommendations returned
- Verify catalog data exists in `backend/data/catalog.json`
- Check backend logs for errors
- Verify API keys are valid (if using API-based embeddings)

### Vector store build fails
- Check if catalog.json exists
- Verify API keys are set (or sentence-transformers is installed)
- Check disk space for storing embeddings

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [APPROACH.md](APPROACH.md) for architecture details
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment

## Getting API Keys

### OpenAI
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Copy and add to `backend/.env`

### Google Gemini
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Create API key
4. Copy and add to `backend/.env`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the README.md
3. Check backend logs for error messages
4. Verify all environment variables are set correctly

