import { useState } from 'react'

function ResultTable({ recommendations }) {
  const [expandedIndex, setExpandedIndex] = useState(null)

  const toggleExpand = (index) => {
    setExpandedIndex(expandedIndex === index ? null : index)
  }

  const getTypeColor = (type) => {
    const colors = {
      'Knowledge & Skills': 'bg-yellow-400/20 text-yellow-400 border-yellow-400/50',
      'Personality & Behavior': 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50',
      'Cognitive Ability': 'bg-yellow-600/20 text-yellow-200 border-yellow-600/50',
      'Other': 'bg-gray-800 text-gray-300 border-gray-700'
    }
    return colors[type] || colors['Other']
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-yellow-400/20">
        <thead>
          <tr className="bg-black/50 border-b-2 border-yellow-400/30">
            <th className="px-6 py-4 text-left text-xs font-bold text-yellow-400 uppercase tracking-wider">
              Rank
            </th>
            <th className="px-6 py-4 text-left text-xs font-bold text-yellow-400 uppercase tracking-wider">
              Assessment Name
            </th>
            <th className="px-6 py-4 text-left text-xs font-bold text-yellow-400 uppercase tracking-wider">
              Type
            </th>
            <th className="px-6 py-4 text-left text-xs font-bold text-yellow-400 uppercase tracking-wider">
              URL
            </th>
            <th className="px-6 py-4 text-left text-xs font-bold text-yellow-400 uppercase tracking-wider">
              Details
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-yellow-400/10">
          {recommendations.map((rec, index) => (
            <tr 
              key={index} 
              className="bg-black/30 hover:bg-black/50 transition-all duration-200 border-l-4 border-transparent hover:border-yellow-400/50 group"
            >
              <td className="px-6 py-4 whitespace-nowrap">
                <span className="text-lg font-bold text-yellow-400 group-hover:text-yellow-300 transition-colors">
                  #{index + 1}
                </span>
              </td>
              <td className="px-6 py-4">
                <span className="text-sm font-semibold text-yellow-50 group-hover:text-yellow-100 transition-colors">
                  {rec.assessment_name}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-3 py-1.5 text-xs font-bold rounded-full border ${getTypeColor(rec.test_type)}`}>
                  {rec.test_type}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                {rec.assessment_url ? (
                  <a
                    href={rec.assessment_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-yellow-400 hover:text-yellow-300 font-semibold transition-colors group/link"
                  >
                    <span className="mr-2">View Assessment</span>
                    <svg className="w-4 h-4 transform group-hover/link:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                ) : (
                  <span className="text-gray-500">N/A</span>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                {rec.description && (
                  <button
                    onClick={() => toggleExpand(index)}
                    className="text-yellow-400 hover:text-yellow-300 font-semibold transition-colors flex items-center group/btn"
                  >
                    <span>{expandedIndex === index ? 'Hide' : 'Show'} Description</span>
                    <svg 
                      className={`w-4 h-4 ml-1 transform transition-transform ${expandedIndex === index ? 'rotate-180' : ''}`}
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Expanded Descriptions */}
      {recommendations.map((rec, index) => (
        expandedIndex === index && rec.description && (
          <div 
            key={`desc-${index}`} 
            className="mt-4 p-6 bg-black/50 rounded-xl border-2 border-yellow-400/30 backdrop-blur-sm animate-in slide-in-from-top-2 duration-300"
          >
            <h4 className="font-bold text-yellow-400 mb-3 text-lg">{rec.assessment_name}</h4>
            <p className="text-sm text-yellow-100/80 leading-relaxed">{rec.description}</p>
          </div>
        )
      ))}
    </div>
  )
}

export default ResultTable

