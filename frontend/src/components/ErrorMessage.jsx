import React from 'react'

export default function ErrorMessage({ message, onRetry }) {
  if (!message) return null

  return (
    <div className="error-banner" id="app-error-banner" role="alert">
      <div className="error-icon">⚠️</div>
      <div className="error-content">
        <h4 className="error-title">Something went wrong</h4>
        <p className="error-message">{message}</p>
      </div>
      {onRetry && (
        <button className="btn-secondary btn-sm" onClick={onRetry} id="retry-btn">
          Try Again
        </button>
      )}
    </div>
  )
}
