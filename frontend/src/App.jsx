import React, { useState, useEffect } from 'react'
import UploadForm from './components/UploadForm'
import LoadingState from './components/LoadingState'
import MatchResults from './components/MatchResults'
import ErrorMessage from './components/ErrorMessage'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ─── Opportunities Browse View ──────────────────────────────────────────────

function OpportunityCard({ opp }) {
  const typeConfig = {
    internship: { label: 'Internship', badgeClass: 'badge-internship', icon: '💼' },
    scholarship: { label: 'Scholarship', badgeClass: 'badge-scholarship', icon: '🎓' },
    grant: { label: 'Grant', badgeClass: 'badge-grant', icon: '💰' },
  }[opp.type] || { label: opp.type, badgeClass: 'badge-internship', icon: '⭐' }

  const isRolling = !opp.deadline || opp.deadline.toLowerCase() === 'rolling'

  return (
    <div className="opp-browse-card" id={`opp-${opp.title.toLowerCase().replace(/[^a-z0-9]/g, '-')}`}>
      <div className="opp-browse-header">
        <span className={`match-type-badge ${typeConfig.badgeClass}`}>
          <span>{typeConfig.icon}</span> {typeConfig.label}
        </span>
        <span className={`match-deadline-badge ${isRolling ? 'rolling' : ''}`}>
          {isRolling ? '🔄 Rolling' : `📅 ${opp.deadline}`}
        </span>
      </div>
      <h3 className="opp-browse-title">{opp.title}</h3>
      <p className="opp-browse-org">{opp.organization}</p>
      <p className="opp-browse-desc">{opp.description}</p>
      {opp.eligibility && (
        <p className="opp-browse-eligibility">
          <strong>Eligibility:</strong> {opp.eligibility}
        </p>
      )}
      {opp.tags && opp.tags.length > 0 && (
        <div className="opp-browse-tags">
          {opp.tags.map((t, i) => (
            <span key={i} className="match-tag-pill">
              #{t}
            </span>
          ))}
        </div>
      )}
      <div className="opp-browse-footer">
        <a
          href={opp.link}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-apply btn-sm"
        >
          View Program ↗
        </a>
      </div>
    </div>
  )
}

function OpportunitiesView() {
  const [opportunities, setOpportunities] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetch(`${API_URL}/api/opportunities`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to load opportunities`)
        return res.json()
      })
      .then((data) => {
        setOpportunities(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  const filtered =
    filter === 'all'
      ? opportunities
      : opportunities.filter((o) => o.type === filter)

  return (
    <div className="opps-browse-container">
      <div className="opps-browse-hero">
        <h2>Curated Global Opportunities</h2>
        <p>Explore 25+ verified scholarships, internships, and grants indexed in our system.</p>
      </div>

      <div className="opps-filters-bar">
        {['all', 'internship', 'scholarship', 'grant'].map((f) => (
          <button
            key={f}
            className={`filter-pill ${filter === f ? 'active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f === 'all'
              ? `All Opportunities (${opportunities.length})`
              : f.charAt(0).toUpperCase() + f.slice(1) + 's'}
          </button>
        ))}
      </div>

      {loading && (
        <div className="browse-loading">
          <span className="spinner spinner-lg" />
          <p>Loading curated opportunities dataset...</p>
        </div>
      )}

      {error && <ErrorMessage message={error} onRetry={() => window.location.reload()} />}

      {!loading && !error && filtered.length === 0 && (
        <div className="card text-center">
          <p>No opportunities found for the selected category.</p>
        </div>
      )}

      <div className="opps-grid" id="opportunities-list">
        {filtered.map((opp, idx) => (
          <OpportunityCard key={idx} opp={opp} />
        ))}
      </div>
    </div>
  )
}

// ─── Main Application Root ──────────────────────────────────────────────────

export default function App() {
  const [navTab, setNavTab] = useState('match') // 'match' | 'browse'
  const [profile, setProfile] = useState(null)
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [lastFile, setLastFile] = useState(null)

  async function executeMatchFlow(profileId, candidateProfile) {
    try {
      const matchRes = await fetch(`${API_URL}/api/match/${profileId}`)
      if (!matchRes.ok) {
        const errData = await matchRes.json().catch(() => ({}))
        throw new Error(errData.detail || `Matching engine returned HTTP ${matchRes.status}`)
      }
      const matchData = await matchRes.json()
      setMatches(Array.isArray(matchData) ? matchData : matchData.matches || [])
      setProfile(candidateProfile)
    } catch (err) {
      setError(err.message || 'Error computing semantic matches')
    } finally {
      setLoading(false)
    }
  }

  async function handleUpload(file) {
    setLoading(true)
    setError(null)
    setProfile(null)
    setMatches([])
    setLastFile(file)

    const formData = new FormData()
    formData.append('file', file)

    try {
      // 1. Upload CV & Extract Profile
      const uploadRes = await fetch(`${API_URL}/api/cv/upload`, {
        method: 'POST',
        body: formData,
      })
      const uploadData = await uploadRes.json()
      if (!uploadRes.ok) {
        throw new Error(uploadData.detail || `Upload failed with HTTP ${uploadRes.status}`)
      }

      const profileId = uploadData.profile_id || uploadData.id
      const candidateProfile = uploadData.profile || uploadData

      if (!profileId) {
        throw new Error('Profile was extracted but no valid profile ID was returned.')
      }

      // 2. Fetch Semantic Matches with Grounded Explanations
      await executeMatchFlow(profileId, candidateProfile)
    } catch (err) {
      setError(err.message || 'Failed to analyze CV document')
      setLoading(false)
    }
  }

  // Quick-test flow with sample student profile
  async function handleSampleTest() {
    setLoading(true)
    setError(null)
    setProfile(null)
    setMatches([])

    try {
      // Try existing Sarah Connor profile in MongoDB
      const res = await fetch(`${API_URL}/api/match/6ab7ec317e261dcd945c3be3`)
      if (res.ok) {
        const matchData = await res.json()
        setMatches(matchData)
        setProfile({
          name: 'Sarah Connor',
          email: 'sarah.connor@example.com',
          skills: ['Python', 'FastAPI', 'React', 'Machine Learning', 'Git', 'Robotics'],
          summary: 'Motivated Computer Science undergraduate with hands-on full stack and machine learning development experience.',
          interests: ['Artificial Intelligence', 'Robotics', 'Open Source Development'],
          education: [
            {
              institution: 'Tech Institute',
              degree: 'Bachelor of Science',
              field: 'Computer Science & Robotics',
              year: '2020–2024',
            },
          ],
          experience: [
            {
              organisation: 'Cyberdyne Systems',
              role: 'Software Developer Intern',
              duration: 'Jun 2023 – Sep 2023',
              description: 'Contributed to internal API microservices and robotics data pipelines.',
            },
          ],
        })
        setLoading(false)
        return
      }

      // Fallback: Upload a mock CV if ID not found
      throw new Error('Sample profile not found. Please upload a real CV file.')
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  function handleReset() {
    setProfile(null)
    setMatches([])
    setError(null)
    setLoading(false)
    setLastFile(null)
  }

  return (
    <div className="app-layout">
      {/* Top Navigation Bar */}
      <header className="navbar">
        <div className="navbar-container">
          <div className="brand" onClick={handleReset} role="button" tabIndex={0}>
            <span className="brand-logo-icon">🎯</span>
            <div className="brand-text">
              <h1 className="brand-name">Ace-Opportunity</h1>
              <span className="brand-tag">AI Career Matcher</span>
            </div>
          </div>

          <nav className="nav-menu">
            <button
              id="nav-tab-match"
              className={`nav-tab ${navTab === 'match' ? 'active' : ''}`}
              onClick={() => {
                setNavTab('match')
                setError(null)
              }}
            >
              Match CV
            </button>
            <button
              id="nav-tab-browse"
              className={`nav-tab ${navTab === 'browse' ? 'active' : ''}`}
              onClick={() => {
                setNavTab('browse')
                setError(null)
              }}
            >
              Browse Opportunities
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="main-content">
        {navTab === 'match' && (
          <div className="match-flow-wrapper">
            {error && (
              <ErrorMessage
                message={error}
                onRetry={lastFile ? () => handleUpload(lastFile) : handleReset}
              />
            )}

            {loading ? (
              <LoadingState />
            ) : matches.length > 0 && profile ? (
              <MatchResults
                profile={profile}
                matches={matches}
                onReset={handleReset}
              />
            ) : (
              <UploadForm
                onUpload={handleUpload}
                onSampleSelect={handleSampleTest}
                loading={loading}
              />
            )}
          </div>
        )}

        {navTab === 'browse' && <OpportunitiesView />}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>
          Ace-Opportunity &bull; Built with FastAPI, MongoDB Atlas, SentenceTransformers &amp; Google Gemini Flash.
        </p>
      </footer>
    </div>
  )
}