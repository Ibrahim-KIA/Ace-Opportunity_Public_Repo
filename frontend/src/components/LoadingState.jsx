import React, { useState, useEffect } from 'react'

const STAGES = [
  {
    title: 'Parsing document',
    desc: 'Extracting text and structure from your uploaded CV...',
  },
  {
    title: 'Analyzing background',
    desc: 'Identifying your core skills, education, and career experience...',
  },
  {
    title: 'Generating embeddings',
    desc: 'Transforming your profile into a dense semantic vector representation...',
  },
  {
    title: 'Scanning opportunities',
    desc: 'Matching vector similarity against 25+ verified scholarships, internships, and grants...',
  },
  {
    title: 'Personalizing rationales',
    desc: 'Synthesizing tailored "Why You Fit" AI explanations citing your actual background...',
  },
]

export default function LoadingState() {
  const [stageIndex, setStageIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setStageIndex((prev) => (prev < STAGES.length - 1 ? prev + 1 : prev))
    }, 2400)
    return () => clearInterval(interval)
  }, [])

  const currentStage = STAGES[stageIndex]
  const progressPercent = Math.round(((stageIndex + 1) / STAGES.length) * 100)

  return (
    <div className="loading-state card" id="loading-state" aria-live="polite">
      <div className="radar-scanner">
        <div className="radar-circle radar-c1" />
        <div className="radar-circle radar-c2" />
        <div className="radar-circle radar-c3" />
        <div className="radar-center">✨</div>
      </div>

      <div className="loading-content">
        <span className="badge badge-accent loading-badge">
          Step {stageIndex + 1} of {STAGES.length}
        </span>
        <h3 className="loading-title">{currentStage.title}</h3>
        <p className="loading-desc">{currentStage.desc}</p>

        <div className="progress-bar-container">
          <div
            className="progress-bar-fill"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        <div className="stages-checklist">
          {STAGES.map((stage, idx) => {
            const isDone = idx < stageIndex
            const isCurrent = idx === stageIndex
            return (
              <div
                key={idx}
                className={`stage-pill ${isDone ? 'done' : ''} ${isCurrent ? 'active' : ''}`}
              >
                <span className="stage-status-icon">
                  {isDone ? '✓' : isCurrent ? '⏳' : '○'}
                </span>
                <span className="stage-name">{stage.title}</span>
              </div>
            )
          })}
        </div>

        <p className="loading-hint">
          Hold tight — we're running real embeddings and AI models to find your best matches.
        </p>
      </div>
    </div>
  )
}
