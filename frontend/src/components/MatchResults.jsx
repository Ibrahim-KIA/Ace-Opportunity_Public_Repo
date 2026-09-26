import React, { useState } from 'react'
import MatchCard from './MatchCard'

export default function MatchResults({ profile, matches, onReset }) {
  const [filter, setFilter] = useState('all')
  const [sortBy, setSortBy] = useState('score') // 'score' | 'deadline'
  const [showFullProfile, setShowFullProfile] = useState(false)

  const candidateName = profile?.name || 'Candidate'
  const skills = profile?.skills || []
  const education = profile?.education || []
  const experience = profile?.experience || []
  const interests = profile?.interests || []

  // Filter matches
  const filteredMatches = matches.filter((m) => {
    if (filter === 'all') return true
    return m.opportunity?.type === filter
  })

  // Sort matches
  const sortedMatches = [...filteredMatches].sort((a, b) => {
    if (sortBy === 'score') {
      return (b.score || 0) - (a.score || 0)
    }
    if (sortBy === 'deadline') {
      const dA = a.opportunity?.deadline || 'zzz'
      const dB = b.opportunity?.deadline || 'zzz'
      return dA.localeCompare(dB)
    }
    return 0
  })

  return (
    <div className="match-results-container" id="match-results-view">
      {/* Candidate Profile Summary Card */}
      <div className="profile-summary-banner card">
        <div className="profile-summary-header">
          <div className="profile-avatar">
            {candidateName[0].toUpperCase()}
          </div>
          <div className="profile-identity">
            <span className="profile-role-tag">Candidate Profile</span>
            <h2 className="profile-name">{candidateName}</h2>
            {profile?.email && <p className="profile-email">{profile.email}</p>}
          </div>
          <div className="profile-banner-actions">
            <button
              className="btn-secondary btn-sm"
              onClick={() => setShowFullProfile(!showFullProfile)}
              id="toggle-profile-btn"
            >
              {showFullProfile ? 'Hide Profile Details ▲' : 'View Extracted Profile ▼'}
            </button>
            <button className="btn-ghost-sm" onClick={onReset} id="upload-new-cv-btn">
              ← Upload New CV
            </button>
          </div>
        </div>

        {/* Highlighted Skills */}
        {skills.length > 0 && (
          <div className="profile-skills-row">
            <span className="skills-label">Extracted Skills:</span>
            <div className="skills-badge-list">
              {skills.map((s, i) => (
                <span key={i} className="badge badge-skill">
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Expandable Profile Details Drawer */}
        {showFullProfile && (
          <div className="profile-full-drawer">
            {profile?.summary && (
              <div className="profile-drawer-section">
                <h4>Professional Summary</h4>
                <p className="summary-text">{profile.summary}</p>
              </div>
            )}

            {interests.length > 0 && (
              <div className="profile-drawer-section">
                <h4>Interests &amp; Aims</h4>
                <div className="skills-badge-list">
                  {interests.map((it, i) => (
                    <span key={i} className="badge badge-interest">
                      {it}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {education.length > 0 && (
              <div className="profile-drawer-section">
                <h4>Education</h4>
                <ul className="timeline">
                  {education.map((e, i) => (
                    <li key={i} className="timeline-item">
                      <span className="timeline-dot" />
                      <div>
                        <p className="timeline-title">{e.institution}</p>
                        <p className="timeline-sub">
                          {[e.degree, e.field].filter(Boolean).join(' · ')}
                          {e.year && ` (${e.year})`}
                        </p>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {experience.length > 0 && (
              <div className="profile-drawer-section">
                <h4>Experience</h4>
                <ul className="timeline">
                  {experience.map((ex, i) => {
                    const org = ex.organisation || ex.organization || ''
                    return (
                      <li key={i} className="timeline-item">
                        <span className="timeline-dot" />
                        <div>
                          <p className="timeline-title">
                            {ex.role} {org && <span className="org">@ {org}</span>}
                          </p>
                          {ex.duration && <p className="timeline-sub">{ex.duration}</p>}
                          {ex.description && <p className="timeline-desc">{ex.description}</p>}
                        </div>
                      </li>
                    )
                  })}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Results Header with Controls */}
      <div className="results-controls-bar">
        <div className="results-heading">
          <h3 className="section-title">
            Top {matches.length} Matched Opportunities
          </h3>
          <p className="section-subtitle">
            Ranked by dense semantic similarity with grounded AI explanations
          </p>
        </div>

        <div className="filter-sort-controls">
          {/* Type Filter Pills */}
          <div className="filter-pill-group">
            {['all', 'internship', 'scholarship', 'grant'].map((f) => (
              <button
                key={f}
                className={`filter-pill ${filter === f ? 'active' : ''}`}
                onClick={() => setFilter(f)}
                id={`filter-${f}`}
              >
                {f === 'all'
                  ? `All (${matches.length})`
                  : f.charAt(0).toUpperCase() + f.slice(1) + 's'}
              </button>
            ))}
          </div>

          {/* Sort selector */}
          <div className="sort-group">
            <label htmlFor="sort-select" className="sort-label">
              Sort by:
            </label>
            <select
              id="sort-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="select-sort"
            >
              <option value="score">Highest Match Score</option>
              <option value="deadline">Application Deadline</option>
            </select>
          </div>
        </div>
      </div>

      {/* Matches Grid */}
      {sortedMatches.length > 0 ? (
        <div className="matches-grid" id="matches-grid">
          {sortedMatches.map((match, index) => (
            <MatchCard key={index} match={match} rank={index + 1} />
          ))}
        </div>
      ) : (
        <div className="no-matches-card card">
          <p className="no-matches-icon">🔍</p>
          <h4>No matches found for filter: "{filter}"</h4>
          <p>Try switching to "All" to view all available opportunities.</p>
          <button className="btn-secondary" onClick={() => setFilter('all')}>
            Show All Opportunities
          </button>
        </div>
      )}

      {/* Footer restart CTA */}
      <div className="results-bottom-cta">
        <button className="btn-secondary btn-lg" onClick={onReset} id="bottom-reset-btn">
          ← Upload Another CV or Profile
        </button>
      </div>
    </div>
  )
}
