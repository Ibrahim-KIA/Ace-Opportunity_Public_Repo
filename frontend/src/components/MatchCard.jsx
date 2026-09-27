import React, { useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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

export default function MatchCard({ match, rank, profile }) {
  const opp = match.opportunity || {}
  const rawScore = typeof match.score === 'number' ? match.score : 0.5

  // Normalize dense embedding score into user-friendly match percentage
  let displayPercent = Math.round(Math.min(98, Math.max(50, (rawScore / 0.52) * 94)))
  if (rawScore >= 0.50) displayPercent = Math.min(99, Math.round(92 + (rawScore - 0.50) * 20))

  const typeConfig = TYPE_CONFIG[opp.type] || {
    label: opp.type || 'Opportunity',
    badgeClass: 'badge-internship',
    icon: '⭐',
  }

  const isRolling = !opp.deadline || opp.deadline.toLowerCase() === 'rolling'
  const cardId = `match-card-${rank}`

  // ─── Checklist State ────────────────────────────────────────────────────────
  const [showChecklist, setShowChecklist] = useState(false)
  const [checklist, setChecklist] = useState(null)
  const [checklistLoading, setChecklistLoading] = useState(false)
  const [checklistError, setChecklistError] = useState(null)
  const [checkedDocs, setCheckedDocs] = useState({})

  async function fetchChecklist() {
    setChecklistLoading(true)
    setChecklistError(null)

    try {
      const res = await fetch(`${API_URL}/api/checklist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile_id: profile?.id || profile?.profile_id,
          profile: profile,
          opportunity_id: opp?._id || opp?.title,
          opportunity: opp,
        }),
      })

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || `Server returned HTTP ${res.status}`)
      }

      const data = await res.json()
      setChecklist(data)
    } catch (err) {
      setChecklistError(err.message || 'Failed to generate prep checklist')
    } finally {
      setChecklistLoading(false)
    }
  }

  function handleToggleChecklist() {
    if (!showChecklist && !checklist && !checklistLoading) {
      fetchChecklist()
    }
    setShowChecklist(!showChecklist)
  }

  function toggleDoc(index) {
    setCheckedDocs((prev) => ({
      ...prev,
      [index]: !prev[index],
    }))
  }

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

      {/* Footer & Action Controls */}
      <div className="match-footer">
        <button
          type="button"
          className={`btn-checklist-toggle ${showChecklist ? 'active' : ''}`}
          onClick={handleToggleChecklist}
          id={`checklist-btn-${rank}`}
        >
          {checklistLoading ? (
            <>
              <span className="spinner spinner-xs" /> Synthesizing Checklist...
            </>
          ) : showChecklist ? (
            <>📋 Hide Prep Checklist ▲</>
          ) : (
            <>📋 Actionable Prep Checklist ✨</>
          )}
        </button>

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

      {/* Expandable Actionable Prep Checklist Drawer */}
      {showChecklist && (
        <div className="checklist-drawer" id={`checklist-drawer-${rank}`}>
          <div className="checklist-drawer-header">
            <div className="checklist-header-title">
              <span className="checklist-badge">AI Application Strategy</span>
              <h4>Preparation Checklist</h4>
            </div>
            <p className="checklist-subtitle">
              Personalized materials, timeline advice, and concrete action steps tailored for{' '}
              <strong>{opp.title}</strong>.
            </p>
          </div>

          {checklistLoading && (
            <div className="checklist-loading-box">
              <span className="spinner spinner-md" />
              <p>Analyzing candidate profile and tailoring required materials...</p>
            </div>
          )}

          {checklistError && (
            <div className="checklist-error-box">
              <p>⚠️ {checklistError}</p>
              <button
                type="button"
                className="btn-secondary btn-sm"
                onClick={fetchChecklist}
              >
                Retry
              </button>
            </div>
          )}

          {checklist && !checklistLoading && (
            <div className="checklist-content">
              {/* Strategic Deadline Note */}
              {checklist.deadline_note && (
                <div className="checklist-deadline-box">
                  <span className="deadline-box-icon">⏱️</span>
                  <div className="deadline-box-content">
                    <span className="deadline-box-title">Timeline &amp; Submission Strategy</span>
                    <p className="deadline-box-text">{checklist.deadline_note}</p>
                  </div>
                </div>
              )}

              {/* Required Documents Interactive List */}
              {checklist.documents && checklist.documents.length > 0 && (
                <div className="checklist-block">
                  <h5 className="checklist-block-title">
                    Required Materials &amp; Documents
                  </h5>
                  <div className="interactive-docs-list">
                    {checklist.documents.map((doc, idx) => {
                      const isChecked = !!checkedDocs[idx]
                      return (
                        <label
                          key={idx}
                          className={`doc-check-item ${isChecked ? 'doc-checked' : ''}`}
                        >
                          <input
                            type="checkbox"
                            className="doc-checkbox"
                            checked={isChecked}
                            onChange={() => toggleDoc(idx)}
                          />
                          <span className="doc-check-box-custom">
                            {isChecked ? '✓' : ''}
                          </span>
                          <span className="doc-text">{doc}</span>
                        </label>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Tailored Prep Tips */}
              {checklist.tips && checklist.tips.length > 0 && (
                <div className="checklist-block">
                  <h5 className="checklist-block-title">Strategic Preparation Tips</h5>
                  <div className="tips-list">
                    {checklist.tips.map((tip, idx) => (
                      <div key={idx} className="tip-card">
                        <span className="tip-badge">{idx + 1}</span>
                        <p className="tip-text">{tip}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
