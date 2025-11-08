# Environment Variables Template

Copy these to `.env` files in the respective directories.

## Backend (.env in `backend/` directory)

```env
# OpenAI API Key (for embeddings and reranking)
# Get your key at: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini API Key (alternative to OpenAI)
# Get your key at: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Enable/disable LLM reranking (true/false)
# Set to false to disable reranking and save API costs
ENABLE_RERANKING=true
```

**Note:** You need at least one of `OPENAI_API_KEY` or `GEMINI_API_KEY`. If neither is provided, the system will use a local fallback model (sentence-transformers), which may have lower quality but works for testing.

## Frontend (.env in `frontend/` directory)

```env
# Backend API URL
# For local development: http://localhost:8000
# For production: https://your-backend-url.onrender.com
VITE_API_URL=http://localhost:8000
```

## Instructions

1. **Backend Setup:**
   ```bash
   cd backend
   cp ../ENV_TEMPLATE.md .env
   # Edit .env and add your API keys
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   echo "VITE_API_URL=http://localhost:8000" > .env
   # For production, update with your backend URL
   ```

3. **Never commit .env files** - They are already in .gitignore

