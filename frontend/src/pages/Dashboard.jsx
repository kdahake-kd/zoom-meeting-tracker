import React, { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { meetingsAPI } from '../services/api'
import './Dashboard.css'

function Dashboard() {
  const [meetings, setMeetings] = useState([])
  const [zoomMeetings, setZoomMeetings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showZoomMeetings, setShowZoomMeetings] = useState(false)
  const [syncing, setSyncing] = useState({})
  const [searchParams] = useSearchParams()

  useEffect(() => {
    fetchMeetings()
    
    // Check if redirected from auth
    if (searchParams.get('auth') === 'success') {
      alert('Successfully authenticated with Zoom!')
      // Remove query param from URL
      window.history.replaceState({}, '', window.location.pathname)
    }
  }, [])

  const fetchMeetings = async () => {
    try {
      setLoading(true)
      const response = await meetingsAPI.getAll()
      const meetingsList = response.data.meetings || []
      setMeetings(meetingsList)
      setError(null)
      console.log('Fetched meetings:', meetingsList.length, meetingsList)
      return meetingsList
    } catch (err) {
      setError('Failed to load meetings. Make sure you are authenticated.')
      console.error('Error fetching meetings:', err)
      return []
    } finally {
      setLoading(false)
    }
  }

  const fetchZoomMeetings = async (meetingType = 'past') => {
    try {
      setLoading(true)
      setError(null)
      const response = await meetingsAPI.listFromZoom(meetingType)
      
      if (response.data) {
        if (response.data.meetings && Array.isArray(response.data.meetings)) {
          setZoomMeetings(response.data.meetings)
          setShowZoomMeetings(true)
          if (response.data.meetings.length === 0) {
            if (meetingType === 'past') {
              setError('No past meetings found. Try creating a meeting first, or check "Live" or "Upcoming" meetings.')
            } else {
              setError(`No ${meetingType} meetings found.`)
            }
          }
        } else {
          setZoomMeetings([])
          setShowZoomMeetings(true)
          setError(response.data.message || 'No meetings returned from Zoom API.')
        }
      } else {
        setZoomMeetings([])
        setShowZoomMeetings(true)
        setError('Invalid response from server.')
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.response?.data?.message || err.message || 'Unknown error'
      setError(`Failed to load meetings from Zoom: ${errorMsg}`)
      console.error('Error fetching Zoom meetings:', err)
      console.error('Full error response:', err.response?.data)
      setZoomMeetings([])
      setShowZoomMeetings(false)
    } finally {
      setLoading(false)
    }
  }

  const handleSyncMeeting = async (meetingId) => {
    try {
      setSyncing({ ...syncing, [meetingId]: true })
      const response = await meetingsAPI.sync(meetingId)
      console.log('Sync response:', response.data)
      
      // Wait a moment for database to update
      await new Promise(resolve => setTimeout(resolve, 800))
      
      // Force refresh synced meetings list
      const updatedMeetings = await fetchMeetings()
      console.log('Updated meetings after sync:', updatedMeetings)
      
      // Check if meeting was actually added
      const syncedMeeting = updatedMeetings.find(m => m.meeting_id === meetingId || m.meeting_id === String(meetingId))
      
      if (syncedMeeting) {
        // Scroll to synced meetings section after a brief delay
        setTimeout(() => {
          const syncedSection = document.querySelector('.synced-meetings-section')
          if (syncedSection) {
            syncedSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
            // Highlight the section briefly
            syncedSection.style.border = '3px solid #10b981'
            setTimeout(() => {
              syncedSection.style.border = ''
            }, 2000)
          }
        }, 300)
      } else {
        console.warn('Meeting not found in updated list, forcing page refresh')
        // Force a full page refresh as last resort
        window.location.reload()
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.response?.data?.message || err.message
      alert('Failed to sync meeting: ' + errorMsg)
      console.error('Error syncing meeting:', err)
      console.error('Full error:', err.response?.data)
    } finally {
      setSyncing({ ...syncing, [meetingId]: false })
    }
  }

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A'
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    if (hours > 0) {
      return `${hours}h ${minutes}m`
    }
    return `${minutes}m`
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString()
  }

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading">Loading meetings...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="dashboard">
        <div className="error">{error}</div>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Meetings</h2>
        <div className="header-actions">
          <div className="meeting-type-buttons">
            <button onClick={() => fetchZoomMeetings('past')} className="sync-button small">
              Load Past
            </button>
            <button onClick={() => fetchZoomMeetings('live')} className="sync-button small">
              Load Live
            </button>
            <button onClick={() => fetchZoomMeetings('upcoming')} className="sync-button small">
              Load Upcoming
            </button>
          </div>
          <button onClick={fetchMeetings} className="refresh-button">
            Refresh
          </button>
        </div>
      </div>

      {showZoomMeetings && (
        <div className="zoom-meetings-section">
          <div className="section-header-with-close">
            <h3>
              {zoomMeetings.length > 0 
                ? `Available Meetings from Zoom (${zoomMeetings.length} found)`
                : 'Available Meetings from Zoom'
              }
            </h3>
            <button 
              onClick={() => {
                setShowZoomMeetings(false)
                setZoomMeetings([])
                setError(null)
              }}
              className="close-button"
              title="Close and return to main view"
            >
              ✕ Close
            </button>
          </div>
          {zoomMeetings.length > 0 ? (
            <div className="meetings-grid">
            {zoomMeetings.map((meeting) => (
              <div key={meeting.meeting_id} className="meeting-card zoom-meeting">
                <div className="meeting-card-header">
                  <h3>{meeting.topic || 'Untitled Meeting'}</h3>
                  <span className="meeting-id">ID: {meeting.meeting_id}</span>
                </div>
                <div className="meeting-card-body">
                  <div className="meeting-stat">
                    <span className="stat-label">Start Time:</span>
                    <span className="stat-value">{formatDate(meeting.start_time)}</span>
                  </div>
                  <div className="meeting-stat">
                    <span className="stat-label">Duration:</span>
                    <span className="stat-value">{formatDuration(meeting.duration)}</span>
                  </div>
                  <button
                    onClick={() => handleSyncMeeting(meeting.meeting_id)}
                    disabled={syncing[meeting.meeting_id]}
                    className="sync-meeting-button"
                  >
                    {syncing[meeting.meeting_id] ? 'Syncing...' : 'Sync This Meeting'}
                  </button>
                </div>
              </div>
            ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>No meetings found. Try a different meeting type or create a new meeting in Zoom.</p>
            </div>
          )}
        </div>
      )}

      <div className="synced-meetings-section" id="synced-meetings">
        <div className="section-header-with-count">
          <h3>Synced Meetings {meetings.length > 0 && `(${meetings.length})`}</h3>
          <button onClick={fetchMeetings} className="refresh-button small">
            Refresh
          </button>
        </div>
        {meetings.length === 0 ? (
          <div className="empty-state">
            <p>No synced meetings found. Click "Load Past/Live/Upcoming" above to see available meetings, then click "Sync This Meeting" to add them here.</p>
            <p style={{marginTop: '1rem', fontSize: '0.875rem', color: '#6b7280'}}>
              If you just synced a meeting, try clicking "Refresh" above or refresh the page.
            </p>
          </div>
        ) : (
          <div className="meetings-grid">
            {meetings.map((meeting) => (
              <Link
                key={meeting.id}
                to={`/meeting/${meeting.meeting_id}`}
                className="meeting-card"
              >
                <div className="meeting-card-header">
                  <h3>{meeting.topic || 'Untitled Meeting'}</h3>
                  <span className="meeting-id">ID: {meeting.meeting_id}</span>
                </div>
                <div className="meeting-card-body">
                  <div className="meeting-stat">
                    <span className="stat-label">Participants:</span>
                    <span className="stat-value">{meeting.participant_count || 0}</span>
                  </div>
                  <div className="meeting-stat">
                    <span className="stat-label">Duration:</span>
                    <span className="stat-value">{formatDuration(meeting.duration)}</span>
                  </div>
                  <div className="meeting-stat">
                    <span className="stat-label">Start Time:</span>
                    <span className="stat-value">{formatDate(meeting.start_time)}</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard

