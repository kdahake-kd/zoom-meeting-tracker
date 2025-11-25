import React, { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { authAPI } from '../services/api'
import './Auth.css'

function Auth() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const code = searchParams.get('code')

  useEffect(() => {
    if (code) {
      // Handle OAuth callback
      handleCallback()
    } else {
      // Initiate OAuth flow
      initiateAuth()
    }
  }, [code])

  const initiateAuth = async () => {
    try {
      const response = await authAPI.getAuthUrl()
      window.location.href = response.data.auth_url
    } catch (error) {
      console.error('Auth error:', error)
    }
  }

  const handleCallback = async () => {
    // The callback is handled by the backend
    // Just redirect to home
    setTimeout(() => {
      navigate('/')
    }, 2000)
  }

  if (code) {
    return (
      <div className="auth-page">
        <div className="auth-container">
          <h2>Authentication Successful!</h2>
          <p>Redirecting to dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <h2>Connect to Zoom</h2>
        <p>Click the button below to authenticate with Zoom</p>
        <button onClick={initiateAuth} className="auth-button">
          Connect Zoom Account
        </button>
      </div>
    </div>
  )
}

export default Auth

