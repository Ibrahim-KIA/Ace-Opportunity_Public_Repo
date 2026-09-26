import React, { useState, useRef } from 'react'

const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5 MB

export default function UploadForm({ onUpload, onSampleSelect, loading }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [validationError, setValidationError] = useState(null)

  function validateAndSetFile(file) {
    setValidationError(null)
    if (!file) return

    const ext = file.name.split('.').pop().toLowerCase()
    if (!['pdf', 'docx'].includes(ext)) {
      setValidationError('Please upload a PDF (.pdf) or Word document (.docx).')
      setSelectedFile(null)
      return
    }

    if (file.size > MAX_FILE_SIZE) {
      setValidationError('File is too large. Maximum allowed size is 5 MB.')
      setSelectedFile(null)
      return
    }

    setSelectedFile(file)
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0])
    }
  }

  function handleChange(e) {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0])
    }
  }

  function handleSubmit(e) {
    e.preventDefault()
    if (!selectedFile) {
      setValidationError('Please select a CV file first.')
      return
    }
    onUpload(selectedFile)
  }

  function formatFileSize(bytes) {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  return (
    <div className="upload-container card">
      <div className="upload-header">
        <span className="step-indicator">Step 1 of 2</span>
        <h2 className="card-title">Upload your CV / Resume</h2>
        <p className="card-desc">
          Our AI scans your concrete skills, education, and career experience to calculate
          semantic matches against real scholarships, internships, and grants.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="upload-form">
        <div
          id="drop-zone"
          className={`drop-zone ${dragging ? 'dragging' : ''} ${selectedFile ? 'has-file' : ''}`}
          onClick={() => inputRef.current && inputRef.current.click()}
          onDragOver={(e) => {
            e.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              inputRef.current && inputRef.current.click()
            }
          }}
          aria-label="Upload CV file zone"
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
            <div className="file-preview">
              <div className="file-preview-icon">📄</div>
              <div className="file-preview-info">
                <p className="file-name">{selectedFile.name}</p>
                <p className="file-meta">{formatFileSize(selectedFile.size)} · Ready to match</p>
              </div>
              <button
                type="button"
                className="btn-text btn-remove-file"
                onClick={(e) => {
                  e.stopPropagation()
                  setSelectedFile(null)
                  if (inputRef.current) inputRef.current.value = ''
                }}
              >
                Change file
              </button>
            </div>
          ) : (
            <div className="drop-content">
              <div className="upload-icon-circle">
                <span className="upload-icon">📁</span>
              </div>
              <p className="drop-primary">
                <strong>Click to browse</strong> or drag &amp; drop your CV here
              </p>
              <p className="drop-hint">Supports PDF and Word (.docx) · Up to 5 MB</p>
            </div>
          )}
        </div>

        {validationError && (
          <div className="validation-error" id="upload-validation-error">
            <span>⚠️</span> {validationError}
          </div>
        )}

        <div className="upload-actions">
          <button
            type="submit"
            id="upload-submit-btn"
            className="btn-primary btn-lg"
            disabled={!selectedFile || loading}
          >
            {loading ? (
              <>
                <span className="spinner" /> Analyzing &amp; Matching...
              </>
            ) : (
              'Analyze & Find Matches →'
            )}
          </button>
        </div>
      </form>

      {onSampleSelect && (
        <div className="sample-quick-pick">
          <span className="sample-label">Want a quick test?</span>
          <button
            type="button"
            id="sample-cv-btn"
            className="btn-ghost-sm"
            onClick={onSampleSelect}
            disabled={loading}
          >
            ⚡ Test with sample CS &amp; Robotics CV (Sarah Connor)
          </button>
        </div>
      )}
    </div>
  )
}
