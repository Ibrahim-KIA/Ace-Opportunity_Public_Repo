import { useState, useRef } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ─── helpers ────────────────────────────────────────────────────────────────

function Badge({ text, variant = 'skill' }) {
  return <span className={`badge badge-${variant}`}>{text}</span>
}

function SectionHeading({ children }) {
  return <h3 className="section-heading">{children}</h3>
}

// ─── profile display ─────────────────────────────────────────────────────────

function ProfileCard({ profile }) {
  const education = profile.education || []
  const experience = profile.experience || []
  const skills = profile.skills || []
  const interests = profile.interests || []

  return (
    <div className="profile-card" id="profile-card">
      {/* Header */}
      <div className="profile-header">
        <div className="avatar">{profile.name ? profile.name[0].toUpperCase() : '?'}</div>
        <div>
          <h2 className="profile-name">{profile.name || 'Name not found'}</h2>
          {profile.email && <p className="profile-email">{profile.email}</p>}
        </div>
      </div>

      {/* Summary */}
      {profile.summary && (
        <div className="profile-section">
          <SectionHeading>Summary</SectionHeading>
          <p className="summary-text">{profile.summary}</p>
        </div>
      )}

      {/* Skills */}
      {skills.length > 0 && (
        <div className="profile-section">
          <SectionHeading>Skills</SectionHeading>
          <div className="badge-row">
            {skills.map((s, i) => <Badge key={i} text={s} variant="skill" />)}
          </div>
        </div>
      )}

      {/* Interests */}
      {interests.length > 0 && (
        <div className="profile-section">
          <SectionHeading>Interests</SectionHeading>
          <div className="badge-row">
            {interests.map((it, i) => <Badge key={i} text={it} variant="interest" />)}
          </div>
        </div>
      )}

      {/* Education */}
      {education.length > 0 && (
        <div className="profile-section">
          <SectionHeading>Education</SectionHeading>
          <ul className="timeline">
            {education.map((e, i) => {
              const years = (e.start_year || e.end_year)
                ? [e.start_year, e.end_year].filter(Boolean).join('–')
                : (e.year || '')
              return (
                <li key={i} className="timeline-item">
                  <span className="timeline-dot" />
                  <div>
                    <p className="timeline-title">{e.institution}</p>
                    <p className="timeline-sub">
                      {[e.degree, e.field].filter(Boolean).join(' · ')}
                      {years && <> &mdash; {years}</>}
                    </p>
                  </div>
                </li>
              )
            })}
          </ul>
        </div>
      )}

      {/* Experience */}
      {experience.length > 0 && (
        <div className="profile-section">
          <SectionHeading>Experience</SectionHeading>
          <ul className="timeline">
            {experience.map((ex, i) => {
              const dates = (ex.start_date || ex.end_date)
                ? [ex.start_date, ex.end_date].filter(Boolean).join(' – ')
                : (ex.duration || '')
              const org = ex.organisation || ex.organization || ''
              return (
                <li key={i} className="timeline-item">
                  <span className="timeline-dot" />
                  <div>
                    <p className="timeline-title">
                      {ex.role} {org && <span className="org">@ {org}</span>}
                    </p>
                    {dates && <p className="timeline-sub">{dates}</p>}
                    {ex.description && <p className="timeline-desc">{ex.description}</p>}
                  </div>
                </li>
              )
            })}
          </ul>
        </div>
      )}
    </div>
  )
}

// ─── upload zone ─────────────────────────────────────────────────────────────

function UploadZone({ onUpload, loading }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)

  function handleFile(file) {
    if (!file) return
    setSelectedFile(file)
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    handleFile(file)
  }

  function handleChange(e) {
    handleFile(e.target.files[0])
  }

  function handleSubmit() {
    if (selectedFile) onUpload(selectedFile)
  }

  return (
    <div className="upload-section">
      <div
        id="drop-zone"
        className={`drop-zone ${dragging ? 'dragging' : ''} ${selectedFile ? 'has-file' : ''}`}
        onClick={() => inputRef.current.click()}
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          style={{ display: 'none' }}
          id="cv-file-input"
          onChange={handleChange}
        />
        {selectedFile ? (
          <>
            <div className="file-icon">📄</div>
            <p className="file-name">{selectedFile.name}</p>
            <p className="drop-hint">Click to change file</p>
          </>
        ) : (
          <>
            <div className="upload-icon">☁️</div>
            <p className="drop-primary">Drop your CV here</p>
            <p className="drop-hint">PDF or DOCX · max 5 MB</p>
          </>
        )}
      </div>

      <button
        id="parse-cv-btn"
        className="btn-primary"
        onClick={handleSubmit}
        disabled={!selectedFile || loading}
      >
        {loading
          ? <><span className="spinner" /> Analyzing your CV with AI…</>
          : 'Parse my CV →'}
      </button>
    </div>
  )
}

// ─── app root ────────────────────────────────────────────────────────────────

export default function App() {
  const [profile, setProfile] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleUpload(file) {
    setLoading(true)
    setError(null)
    setProfile(null)

    const form = new FormData()
    form.append('file', file)

    try {
      const res = await fetch(`${API_URL}/api/cv/upload`, {
        method: 'POST',
        body: form,
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`)
      setProfile(data.profile || data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function handleReset() {
    setProfile(null)
    setError(null)
  }

  return (
    <div className="container">
      <header>
        <h1 className="logo">Ace-Opportunity</h1>
        <p className="tagline">
          AI copilot that matches your CV to real internships, scholarships &amp; grants.
        </p>
      </header>

      <main>
        {!profile ? (
          <div className="card">
            <p className="card-hint">Step 1 — Upload your CV</p>
            <h2 className="card-title">Let's build your profile</h2>
            <p className="card-desc">
              Upload your CV and our AI will extract your skills, education and
              experience in seconds.
            </p>
            <UploadZone onUpload={handleUpload} loading={loading} />

            {error && (
              <div className="result error" id="parse-error">
                <span className="dot red" />
                <p>Error: <strong>{error}</strong></p>
              </div>
            )}
          </div>
        ) : (
          <div>
            <ProfileCard profile={profile} />
            <div className="reset-row">
              <button id="reset-btn" className="btn-ghost" onClick={handleReset}>
                ← Upload a different CV
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
