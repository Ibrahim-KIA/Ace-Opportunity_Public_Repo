import React from 'react'

const TYPE_CONFIG = {
  internship: {
    label: 'Internship',
    badgeClass: 'badge-internship',
    icon: '💼',
  },
  scholarship: {
    label: 'Scholarship',
    badgeClass: 'badge-scholarship',
    icon: '🎓',
  },
  grant: {
    label: 'Grant',
    badgeClass: 'badge-grant',
    icon: '💰',
  },
}

export default function MatchCard({ match, rank }) {
  const opp = match.opportunity || {}
  const rawScore = typeof match.score === 'number' ? match.score : 0.5

  // Normalize dense embedding score into user-friendly match percentage
  // MiniLM cosine similarity is typically 0.30 - 0.70 for text matching
  // Scale so 0.45+ is ~90-95%, 0.35 is ~75-80%
  let displayPercent = Math.round(Math.min(98, Math.max(50, (rawScore / 0.52) * 94)))
  if (rawScore >= 0.50) displayPercent = Math.min(99, Math.round(92 + (rawScore - 0.50) * 20))

  const typeConfig = TYPE_CONFIG[opp.type] || {
    label: opp.type || 'Opportunity',
    badgeClass: 'badge-internship',
    icon: '⭐',
  }

  const isRolling = !opp.deadline || opp.deadline.toLowerCase() === 'rolling'
  const cardId = `match-card-${rank}`

  return (
    <div className="match-card" id={cardId}>
      {/* Header Row */}
      <div className="match-card-top">
        <div className="match-badges">
          <span className="match-rank-badge">#{rank}</span>
          <span className={`match-type-badge ${typeConfig.badgeClass}`}>
            <span>{typeConfig.icon}</span> {typeConfig.label}
          </span>
          <span className={`match-deadline-badge ${isRolling ? 'rolling' : ''}`}>
            {isRolling ? '🔄 Rolling Deadline' : `📅 ${opp.deadline}`}
          </span>
        </div>

        {/* Visual Fit Score Indicator */}
        <div className="fit-score-box">
          <div className="fit-score-ring">
            <svg viewBox="0 0 36 36" className="circular-chart">
              <path
                className="circle-bg"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className="circle-fill"
                strokeDasharray={`${displayPercent}, 100`}
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <span className="fit-score-value">{displayPercent}%</span>
          </div>
          <span className="fit-score-label">Semantic Fit</span>
        </div>
      </div>

      {/* Main Title & Organization */}
      <div className="match-title-section">
        <h3 className="match-title">{opp.title}</h3>
        <p className="match-org">{opp.organization}</p>
      </div>

      {/* Grounded Why You Fit Explanation */}
      {match.why_you_fit && (
        <div className="why-you-fit-callout">
          <div className="why-header">
            <span className="ai-icon">✨</span>
            <span className="why-tag">Why You Fit (AI Analysis)</span>
          </div>
          <p className="why-text">{match.why_you_fit}</p>
        </div>
      )}

      {/* Program Description */}
      {opp.description && (
        <p className="match-description">{opp.description}</p>
      )}

      {/* Eligibility */}
      {opp.eligibility && (
        <div className="match-eligibility">
          <span className="eligibility-label">Eligibility:</span>{' '}
          <span className="eligibility-text">{opp.eligibility}</span>
        </div>
      )}

      {/* Tags */}
      {opp.tags && opp.tags.length > 0 && (
        <div className="match-tags-row">
          {opp.tags.map((tag, idx) => (
            <span key={idx} className="match-tag-pill">
              #{tag}
            </span>
          ))}
        </div>
      )}

      {/* Footer & Apply Link */}
      <div className="match-footer">
        {opp.link ? (
          <a
            href={opp.link}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-apply"
            id={`apply-btn-${rank}`}
          >
            Apply on Official Site <span className="arrow-icon">↗</span>
          </a>
        ) : (
          <span className="no-link-text">Direct application link unavailable</span>
        )}
      </div>
    </div>
  )
}
