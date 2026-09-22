import { useState } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function checkBackend() {
    setLoading(true)
    setResult(null)
    setError(null)
    try {
      const res = await fetch(`${API_URL}/api/health`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <header>
        <h1 className="logo">NextStep</h1>
        <p className="tagline">
          AI copilot that matches your CV to real internships, scholarships and grants.
        </p>
      </header>

      <main>
        <div className="card">
          <p className="card-hint">Day 1 — connection check</p>
          <button
            id="check-backend-btn"
            className="btn-primary"
            onClick={checkBackend}
            disabled={loading}
          >
            {loading ? 'Checking…' : 'Check backend connection'}
          </button>

          {result && (
            <div className="result success" id="health-result">
              <span className="dot green" />
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </div>
          )}

          {error && (
            <div className="result error" id="health-error">
              <span className="dot red" />
              <p>Could not reach backend: <strong>{error}</strong></p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
