import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { authAPI } from '../services/api'
import './Navbar.css'

function Navbar() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuthStatus()
    // Check periodically
    const interval = setInterval(checkAuthStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  const checkAuthStatus = async () => {
    try {
      const response = await authAPI.checkStatus()
      setIsAuthenticated(response.data.authenticated)
    } catch (error) {
      setIsAuthenticated(false)
    } finally {
      setLoading(false)
    }
  }

  const handleAuth = async () => {
    try {
      const response = await authAPI.getAuthUrl()
      window.location.href = response.data.auth_url
    } catch (error) {
      console.error('Auth error:', error)
    }
  }

  const handleDisconnect = async () => {
    if (window.confirm('Are you sure you want to disconnect from Zoom? You will need to authenticate again to use the app.')) {
      try {
        await authAPI.disconnect()
        setIsAuthenticated(false)
        // Reload page to clear any cached data
        window.location.reload()
      } catch (error) {
        console.error('Disconnect error:', error)
        alert('Failed to disconnect. Please try again.')
      }
    }
  }

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <h1>Zoom Meeting Tracker</h1>
        </Link>
        <div className="navbar-actions">
          {!loading && (
            <>
              {isAuthenticated ? (
                <button
                  onClick={handleDisconnect}
                  className="auth-button disconnect"
                  title="Disconnect from Zoom"
                >
                  Disconnect
                </button>
              ) : (
                <button
                  onClick={handleAuth}
                  className="auth-button"
                >
                  Connect Zoom
                </button>
              )}
            </>
          )}
        </div>
      </div>
    </nav>
  )
}

export default Navbar

