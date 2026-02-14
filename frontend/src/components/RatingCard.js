import React from 'react';

function RatingCard({ data }) {
  const getRecommendationColor = (rec) => {
    switch(rec) {
      case 'BUY': return '#22c55e';
      case 'HOLD': return '#f59e0b';
      case 'AVOID': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getRecommendationEmoji = (rec) => {
    switch(rec) {
      case 'BUY': return '✅';
      case 'HOLD': return '⏸️';
      case 'AVOID': return '❌';
      default: return '❓';
    }
  };

  return (
    <div className="rating-card">
      <h2>{data.locality}</h2>

      {/* Score Section */}
      <div className="score-section">
        <div className="main-score">
          <div className="score-circle" style={{
            background: `conic-gradient(#3b82f6 ${data.final_score * 3.6}deg, #e5e7eb 0deg)`
          }}>
            <div className="score-inner">
              <div className="score-value">{data.final_score}</div>
              <div className="score-label">/ 100</div>
            </div>
          </div>
        </div>

        <div className="recommendation" style={{
          backgroundColor: getRecommendationColor(data.recommendation)
        }}>
          <span className="rec-emoji">{getRecommendationEmoji(data.recommendation)}</span>
          <span className="rec-text">{data.recommendation}</span>
        </div>
      </div>

      {/* Confidence */}
      <div className="confidence">
        <strong>Confidence:</strong> {data.confidence}% ({data.confidence_level})
      </div>

      {/* Reasoning */}
      <div className="reasoning">
        <strong>Why?</strong> {data.reasoning}
      </div>

      {/* Component Scores */}
      <div className="component-scores">
        <h3>Component Breakdown</h3>
        {Object.entries(data.component_scores).map(([key, value]) => (
          <div key={key} className="component-bar">
            <div className="component-label">
              {key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')}
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ 
                  width: `${value}%`,
                  backgroundColor: value >= 75 ? '#22c55e' : value >= 50 ? '#f59e0b' : '#ef4444'
                }}
              >
                {value.toFixed(1)}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Insights */}
      <div className="insights">
        <h3>✨ Key Insights</h3>
        <ul>
          {data.key_insights.map((insight, index) => (
            <li key={index}>{insight}</li>
          ))}
        </ul>
      </div>

      {/* Risks */}
      {data.risks && data.risks.length > 0 && (
        <div className="risks">
          <h3>⚠️ Risks & Concerns</h3>
          <ul>
            {data.risks.map((risk, index) => (
              <li key={index}>{risk}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default RatingCard;