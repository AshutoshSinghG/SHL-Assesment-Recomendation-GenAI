import { useState } from 'react'
import axios from 'axios'
import ResultTable from './components/ResultTable'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [query, setQuery] = useState('')
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) {
      setError('Please enter a job description or query')
      return
    }

    setLoading(true)
    setError('')
    setRecommendations([])

    try {
      const response = await axios.post(`${API_URL}/recommend`, {
        query: query.trim(),
        top_k: 10
      })
      setRecommendations(response.data.recommendations || [])
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to get recommendations')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-black">
      {/* Animated background gradient */}
      <div className="fixed inset-0 bg-gradient-to-br from-black via-gray-900 to-black opacity-100"></div>
      <div className="fixed inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,215,0,0.1),transparent_50%)]"></div>
      
      <div className="relative z-10 container mx-auto px-4 py-8">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="text-center mb-10">
            <div className="inline-block mb-4">
              <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-yellow-300 to-yellow-500 mb-3 drop-shadow-[0_0_15px_rgba(255,215,0,0.5)]">
                SHL Assessment
              </h1>
              <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-yellow-300 to-yellow-500 drop-shadow-[0_0_15px_rgba(255,215,0,0.5)]">
                Recommendation System
              </h1>
            </div>
            <div className="w-24 h-1 bg-gradient-to-r from-transparent via-yellow-400 to-transparent mx-auto mb-4"></div>
            <p className="text-lg text-yellow-100/80 font-light">
              AI-powered recommendations for SHL assessments based on job descriptions
            </p>
          </div>

          {/* Search Form */}
          <div className="bg-gradient-to-br from-gray-900/90 to-black/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-yellow-400/20 p-8 mb-8 hover:border-yellow-400/40 transition-all duration-300">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="query" className="block text-sm font-semibold text-yellow-400 mb-3 uppercase tracking-wide">
                  Job Description or Query
                </label>
                <textarea
                  id="query"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Enter a job description, role requirements, or natural language query. For example: 'Hiring for a Python Developer with strong problem-solving skills and team collaboration abilities'"
                  className="w-full px-5 py-4 bg-black/50 border-2 border-gray-800 rounded-xl text-yellow-50 placeholder-yellow-900/50 focus:ring-2 focus:ring-yellow-400 focus:border-yellow-400 resize-none transition-all duration-200 hover:border-gray-700"
                  rows={6}
                  disabled={loading}
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-yellow-400 to-yellow-500 text-black py-4 px-8 rounded-xl font-bold text-lg shadow-lg shadow-yellow-500/50 hover:from-yellow-300 hover:to-yellow-400 hover:shadow-yellow-400/70 focus:outline-none focus:ring-4 focus:ring-yellow-400/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98]"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Getting Recommendations...
                  </span>
                ) : (
                  'Get Recommendations'
                )}
              </button>
            </form>

            {error && (
              <div className="mt-6 p-4 bg-red-900/30 border-2 border-red-500/50 rounded-xl backdrop-blur-sm">
                <p className="text-red-200 text-sm font-medium">{error}</p>
              </div>
            )}
          </div>

          {/* Results */}
          {recommendations.length > 0 && (
            <div className="bg-gradient-to-br from-gray-900/90 to-black/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-yellow-400/20 p-8 hover:border-yellow-400/40 transition-all duration-300">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-yellow-300">
                  Recommended Assessments
                </h2>
                <span className="px-4 py-2 bg-yellow-400/20 border border-yellow-400/50 rounded-full text-yellow-400 font-bold">
                  {recommendations.length}
                </span>
              </div>
              <ResultTable recommendations={recommendations} />
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="bg-gradient-to-br from-gray-900/90 to-black/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-yellow-400/20 p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-yellow-400 border-t-transparent mb-4"></div>
              <p className="text-yellow-200 font-medium">Analyzing your query and finding the best assessments...</p>
            </div>
          )}

          {/* Empty State */}
          {!loading && recommendations.length === 0 && !error && (
            <div className="bg-gradient-to-br from-gray-900/90 to-black/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-yellow-400/20 p-12 text-center">
              <div className="text-6xl mb-4">🔍</div>
              <p className="text-yellow-100/70 text-lg">
                Enter a job description above to get SHL assessment recommendations
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App

