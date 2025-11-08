# Troubleshooting Guide

## OpenAI API Quota Exceeded (Error 429)

If you see an error like:
```
Error code: 429 - {'error': {'message': 'You exceeded your current quota...'}}
```

### Solution 1: Use Sentence Transformers (Recommended for Development)

The system will automatically fall back to sentence-transformers when API quota is exceeded. Make sure sentence-transformers is installed:

```bash
pip install sentence-transformers
```

**Option A: Remove OpenAI API Key (Use Local Model)**
1. Edit `backend/.env`
2. Comment out or remove the `OPENAI_API_KEY` line:
   ```env
   # OPENAI_API_KEY=your_key_here
   ```
3. Restart the backend server
4. The system will automatically use sentence-transformers

**Option B: Let Automatic Fallback Work**
- The system will automatically detect quota errors and fall back to sentence-transformers
- No action needed, just wait for the fallback to activate

### Solution 2: Use Gemini API Instead

1. Get a Gemini API key from https://makersuite.google.com/app/apikey
2. Edit `backend/.env`:
   ```env
   GEMINI_API_KEY=your_gemini_key_here
   # OPENAI_API_KEY=your_openai_key_here  # Comment out OpenAI
   ```
3. Restart the backend server

### Solution 3: Fix OpenAI Quota

1. Check your OpenAI account usage at https://platform.openai.com/usage
2. Add credits or upgrade your plan
3. Restart the backend server

## Embedding Dimension Mismatch

If you see an error about embedding dimension mismatch:

**Solution:** Delete the existing vector store and rebuild:
```bash
# Delete the vector store files
rm backend/data/catalog_embeddings.faiss
rm backend/data/catalog_metadata.json

# Restart the backend (it will rebuild automatically)
```

## Frontend Can't Connect to Backend

**Error:** `Failed to fetch` or CORS errors

**Solution:**
1. Make sure backend is running on `http://localhost:8000`
2. Check `frontend/.env` has:
   ```env
   VITE_API_URL=http://localhost:8000
   ```
3. Restart the frontend dev server

## Vector Store Build Fails

**Error:** `Error initializing recommendation engine`

**Solutions:**
1. **Check catalog file exists:**
   ```bash
   # Make sure catalog.json exists
   ls backend/data/catalog.json
   ```

2. **Regenerate catalog:**
   ```bash
   python scripts/crawl_catalog.py
   ```

3. **Check API keys:**
   - If using OpenAI: Verify `OPENAI_API_KEY` in `backend/.env`
   - If using Gemini: Verify `GEMINI_API_KEY` in `backend/.env`
   - Or remove both to use sentence-transformers

4. **Install sentence-transformers:**
   ```bash
   pip install sentence-transformers
   ```

## Port Already in Use

**Error:** `Address already in use` or `Port 8000 is already in use`

**Solution:**
1. Find and kill the process using port 8000:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   
   # Linux/Mac
   lsof -ti:8000 | xargs kill
   ```

2. Or change the port in `backend/main.py`:
   ```python
   uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
   ```

## Module Not Found Errors

**Error:** `ModuleNotFoundError: No module named 'X'`

**Solution:**
1. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. If using sentence-transformers:
   ```bash
   pip install sentence-transformers
   ```

## Slow Embedding Generation

**Issue:** Embeddings take a long time to generate

**Solutions:**
1. **Use API-based embeddings** (OpenAI or Gemini) - much faster
2. **First-time sentence-transformers:** The model downloads on first use (~80MB)
3. **Use existing vector store:** Once built, embeddings are cached in `.faiss` file

## Recommendations Not Relevant

**Issue:** Recommendations don't match the query

**Solutions:**
1. **Enable reranking:** Make sure `ENABLE_RERANKING=true` in `backend/.env`
2. **Use better queries:** Be more specific in job descriptions
3. **Check catalog data:** Verify `backend/data/catalog.json` has good descriptions

## Python Version Warning

**Warning:** `Python version (3.10.0) which Google will stop supporting...`

**Solution:** This is just a warning, not an error. The system will still work. To fix:
1. Upgrade to Python 3.11+ (recommended)
2. Or ignore the warning (it won't affect functionality)

## Getting Help

If you encounter other issues:

1. Check the backend logs for detailed error messages
2. Verify all environment variables are set correctly
3. Ensure all dependencies are installed
4. Try deleting `node_modules` and `backend/data/*.faiss` and rebuilding

