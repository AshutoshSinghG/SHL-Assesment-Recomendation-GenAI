# Deployment Guide

This guide explains how to deploy the SHL Assessment Recommendation System to production.

## Backend Deployment (Render)

### Prerequisites
- GitHub account
- Render account (sign up at https://render.com)
- API keys (OpenAI or Gemini)

### Steps

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Create Render Web Service**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository

3. **Configure Service**
   - **Name**: `shl-recommendation-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables**
   - `OPENAI_API_KEY` or `GEMINI_API_KEY`
   - `ENABLE_RERANKING=true`

5. **Configure Disk Storage** (optional, for persistent vector store)
   - Add a disk with 1GB storage
   - Mount at `/opt/render/project/src/backend/data`

6. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note the service URL (e.g., `https://shl-recommendation-api.onrender.com`)

### Alternative: Using render.yaml

You can use the `render.yaml` file for infrastructure as code:

1. Commit `render.yaml` to your repository
2. In Render dashboard, go to "Blueprints"
3. Click "New Blueprint"
4. Select your repository
5. Render will automatically detect and use `render.yaml`

## Frontend Deployment (Vercel)

### Prerequisites
- Vercel account (sign up at https://vercel.com)
- Backend API URL

### Steps

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Configure Environment Variables**
   - Update `vercel.json` with your backend URL
   - Or set `VITE_API_URL` in Vercel dashboard

3. **Deploy**
   ```bash
   cd frontend
   vercel
   ```

4. **Follow Prompts**
   - Link to existing project or create new
   - Set root directory to `frontend`
   - Configure environment variables

5. **Alternative: GitHub Integration**
   - Go to https://vercel.com/dashboard
   - Click "Add New Project"
   - Import your GitHub repository
   - Set root directory to `frontend`
   - Add environment variable: `VITE_API_URL` = your backend URL
   - Deploy

### Vercel Configuration

Update `vercel.json`:

```json
{
  "env": {
    "VITE_API_URL": "https://your-backend-url.onrender.com"
  }
}
```

Or set in Vercel dashboard:
- Project → Settings → Environment Variables
- Add `VITE_API_URL` with your backend URL

## Alternative: Hugging Face Spaces

### Backend on Hugging Face Spaces

1. **Create Space**
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Select "Docker" as SDK
   - Name your space

2. **Create Files**
   - Upload backend files
   - Create `Dockerfile`:
     ```dockerfile
     FROM python:3.9-slim
     WORKDIR /app
     COPY backend/requirements.txt .
     RUN pip install -r requirements.txt
     COPY backend/ .
     CMD uvicorn app.main:app --host 0.0.0.0 --port 7860
     ```
   - Create `README.md` with space description

3. **Set Secrets**
   - Go to Space → Settings → Secrets
   - Add `OPENAI_API_KEY` or `GEMINI_API_KEY`

4. **Deploy**
   - Commit and push to Space
   - Hugging Face will build and deploy automatically

## Post-Deployment

### Verify Deployment

1. **Check Backend Health**
   ```bash
   curl https://your-backend-url.onrender.com/health
   ```
   Should return: `{"status":"ok"}`

2. **Test Recommendations**
   ```bash
   curl -X POST https://your-backend-url.onrender.com/recommend \
     -H "Content-Type: application/json" \
     -d '{"query": "Python Developer", "top_k": 5}'
   ```

3. **Check Frontend**
   - Visit your Vercel URL
   - Try a sample query
   - Verify recommendations are displayed

### Troubleshooting

**Backend Issues:**
- Check Render logs for errors
- Verify environment variables are set
- Check if catalog data exists in data directory
- Verify API keys are valid

**Frontend Issues:**
- Check browser console for errors
- Verify `VITE_API_URL` is set correctly
- Check CORS settings in backend
- Verify backend is accessible from frontend domain

**CORS Configuration:**
If frontend is on a different domain, update backend CORS:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-url.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Monitoring

### Render
- View logs in Render dashboard
- Set up alerts for service failures
- Monitor resource usage

### Vercel
- View deployment logs
- Monitor function execution
- Check analytics

## Scaling

### Backend
- Upgrade Render service plan for more resources
- Add more instances for load balancing
- Use Redis for caching (optional)

### Frontend
- Vercel automatically scales
- CDN distribution for fast loading
- Edge functions for API calls (optional)

## Cost Estimation

### Render (Backend)
- Free tier: 750 hours/month
- Starter: $7/month
- Standard: $25/month

### Vercel (Frontend)
- Free tier: Unlimited deployments
- Pro: $20/month (for team features)

### API Costs
- OpenAI: ~$0.02 per 1M tokens (embeddings)
- Gemini: Free tier available, then pay-as-you-go

## Security

1. **API Keys**
   - Never commit API keys to repository
   - Use environment variables
   - Rotate keys regularly

2. **CORS**
   - Restrict CORS to specific domains
   - Don't use wildcard in production

3. **Rate Limiting**
   - Add rate limiting to API (optional)
   - Prevent abuse

4. **HTTPS**
   - Both Render and Vercel provide HTTPS by default
   - Ensure all connections use HTTPS

