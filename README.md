# SHL Assessment Recommendation System

A full-stack Generative AI web application that recommends SHL assessments for any given job description (JD) or natural language query using semantic search and LLM-powered reranking.

## 🎯 Features

- **Semantic Search**: Uses embeddings (OpenAI/Gemini) to find relevant assessments based on job descriptions
- **LLM Reranking**: Optional Gemini 1.5 Pro or GPT-4 reranking for improved accuracy
- **Vector Store**: FAISS-based vector database for fast similarity search
- **REST API**: FastAPI backend with `/health` and `/recommend` endpoints
- **Modern Frontend**: React + TailwindCSS for a beautiful, responsive UI
- **CSV Export**: Evaluation script to generate CSV outputs for test queries

## 🏗️ Architecture

```
┌─────────────┐
│   Frontend  │  React + TailwindCSS
│   (React)   │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│   Backend   │  FastAPI
│   (FastAPI) │
└──────┬──────┘
       │
       ├──► Embeddings (OpenAI/Gemini)
       ├──► Vector Store (FAISS)
       └──► LLM Reranker (Optional)
```

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── embeddings.py        # Embedding generation
│   │   ├── vector_store.py      # FAISS vector store
│   │   ├── reranker.py          # LLM reranking
│   │   └── recommend.py         # Recommendation engine
│   ├── data/                    # Data files (catalog, embeddings)
│   ├── requirements.txt
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css
│   │   └── components/
│   │       └── ResultTable.jsx
│   ├── package.json
│   └── vite.config.js
│
├── scripts/
│   ├── crawl_catalog.py         # Web scraper for SHL catalog
│   ├── evaluate.py              # Evaluation script
│   ├── generate_csv.py          # CSV generation script
│   └── unlabeled_test.csv       # Test queries
│
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- API keys for one of:
  - OpenAI API (for embeddings and reranking)
  - Google Gemini API (for embeddings and reranking)

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd SHL-GenAI
```

2. **Backend Setup**

```bash
cd backend
pip install -r requirements.txt
```

3. **Frontend Setup**

```bash
cd frontend
npm install
```

4. **Environment Variables**

Create a `.env` file in the `backend` directory:

```env
# Choose one or both
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Enable/disable LLM reranking
ENABLE_RERANKING=true
```

Create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=http://localhost:8000
```

### Data Collection

1. **Scrape SHL Catalog**

```bash
cd scripts
python crawl_catalog.py
```

This will generate `backend/data/catalog.json` and `backend/data/catalog.csv` with assessment data.

### Running the Application

1. **Start Backend Server**

```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

2. **Start Frontend Development Server**

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

3. **Test the API**

```bash
# Health check
curl http://localhost:8000/health

# Get recommendations
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "Hiring for Python Developer", "top_k": 10}'
```

## 📊 Evaluation

### Generate CSV Output

```bash
# Make sure backend is running
cd scripts
python evaluate.py --api-url http://localhost:8000 --output evaluation_results.csv
```

This will:
1. Load test queries from `unlabeled_test.csv`
2. Call the `/recommend` endpoint for each query
3. Generate CSV output with `Query` and `Assessment_url` columns

### Custom Test Queries

Edit `scripts/unlabeled_test.csv` to add your own test queries:

```csv
query
Your job description here
Another job description
```

## 🧪 API Endpoints

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

### POST `/recommend`

Get assessment recommendations for a job description.

**Request:**
```json
{
  "query": "Hiring for Python Developer with strong problem-solving skills",
  "top_k": 10
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "assessment_name": "Python Developer Skills Test",
      "assessment_url": "https://www.shl.com/...",
      "test_type": "Knowledge & Skills",
      "description": "Evaluates Python programming abilities..."
    }
  ],
  "query": "Hiring for Python Developer...",
  "count": 10
}
```

## 🚢 Deployment

### Backend (Render)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r backend/requirements.txt`
4. Set start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `OPENAI_API_KEY` or `GEMINI_API_KEY`
   - `ENABLE_RERANKING=true`
6. Deploy

### Frontend (Vercel)

1. Install Vercel CLI: `npm i -g vercel`
2. Navigate to frontend directory: `cd frontend`
3. Deploy: `vercel`
4. Set environment variable:
   - `VITE_API_URL` (your Render backend URL)

### Alternative: Hugging Face Spaces

For backend deployment on Hugging Face Spaces:

1. Create a new Space
2. Upload backend files
3. Create `requirements.txt` in the root
4. Create `app.py` that imports from `app.main`
5. Set environment variables in Space settings

## 🔧 Configuration

### Embedding Provider

The system automatically selects an embedding provider based on available API keys:
1. OpenAI (if `OPENAI_API_KEY` is set)
2. Gemini (if `GEMINI_API_KEY` is set)
3. Sentence Transformers (fallback, local model)

### Reranking

LLM reranking is enabled by default but can be disabled by setting `ENABLE_RERANKING=false`.

The reranker uses:
- Gemini 1.5 Pro (preferred)
- GPT-4 (fallback)

## 📝 Approach Summary

See [APPROACH.md](APPROACH.md) for a detailed 2-page summary of the approach, architecture, and implementation details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- SHL for the assessment catalog
- OpenAI and Google for embedding and LLM APIs
- FastAPI, React, and TailwindCSS communities

