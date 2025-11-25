import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { meetingsAPI } from '../services/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import './MeetingDetail.css'

function MeetingDetail() {
  const { meetingId } = useParams()
  const [meeting, setMeeting] = useState(null)
  const [stats, setStats] = useState(null)
  const [recordings, setRecordings] = useState([])
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)

  useEffect(() => {
    fetchMeetingData()
  }, [meetingId])

  const fetchMeetingData = async () => {
    try {
      setLoading(true)
      console.log('Fetching meeting data for:', meetingId)
      const [meetingRes, statsRes, recordingsRes] = await Promise.all([
        meetingsAPI.getById(meetingId),
        meetingsAPI.getStats(meetingId),
        meetingsAPI.getRecordings(meetingId)
      ])
      console.log('Meeting data fetched:', meetingRes.data)
      setMeeting(meetingRes.data)
      setStats(statsRes.data)
      setRecordings(recordingsRes.data.recordings || [])
    } catch (error) {
      console.error('Error fetching meeting data:', error)
      console.error('Full error:', error.response?.data)
      alert('Failed to load meeting data: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleSync = async () => {
    try {
      setSyncing(true)
      console.log('Starting sync for meeting:', meetingId)
      const response = await meetingsAPI.sync(meetingId)
      console.log('Sync response:', response.data)
      
      // Wait a moment for data to be saved
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Refresh meeting data
      await fetchMeetingData()
      
      // Show success message
      alert('Meeting synced successfully! Data has been updated.')
    } catch (error) {
      console.error('Error syncing meeting:', error)
      const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error'
      alert(`Failed to sync meeting: ${errorMsg}`)
    } finally {
      setSyncing(false)
    }
  }

  const handleSyncParticipants = async () => {
    try {
      setSyncing(true)
      console.log('Syncing participants for meeting:', meetingId)
      const response = await meetingsAPI.syncParticipants(meetingId)
      console.log('Participants sync response:', response.data)
      
      // Wait a moment
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Refresh meeting data
      await fetchMeetingData()
      
      // Show success message
      const participantCount = response.data?.participants?.length || 0
      if (participantCount === 0) {
        alert('Participants synced successfully!\n\nNote: Participant data requires a paid Zoom account for past meetings. This is expected for free Zoom accounts.\n\nYour meeting information is still saved and available.')
      } else {
        alert(`Successfully synced ${participantCount} participant(s)!`)
      }
    } catch (error) {
      console.error('Error syncing participants:', error)
      const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error'
      alert(`Failed to sync participants: ${errorMsg}`)
    } finally {
      setSyncing(false)
    }
  }

  const handleSyncRecordings = async () => {
    try {
      setSyncing(true)
      console.log('Syncing recordings for meeting:', meetingId)
      const response = await meetingsAPI.syncRecordings(meetingId)
      console.log('Recordings sync response:', response.data)
      
      // Wait a moment
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Refresh meeting data
      await fetchMeetingData()
      
      // Show success message
      const recordingCount = response.data?.recordings?.length || 0
      if (recordingCount === 0) {
        alert('Recordings synced. No recordings found for this meeting.')
      } else {
        alert(`Successfully synced ${recordingCount} recording(s)!`)
      }
    } catch (error) {
      console.error('Error syncing recordings:', error)
      const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error'
      alert(`Failed to sync recordings: ${errorMsg}`)
    } finally {
      setSyncing(false)
    }
  }

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A'
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`
    }
    return `${minutes}m ${secs}s`
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString()
  }

  if (loading) {
    return <div className="meeting-detail loading">Loading meeting details...</div>
  }

  if (!meeting) {
    return <div className="meeting-detail error">Meeting not found</div>
  }

  const participants = meeting.participants || []
  const chartData = participants
    .filter(p => p.duration)
    .map(p => ({
      name: p.user_name || p.user_email || 'Unknown',
      duration: Math.floor(p.duration / 60) // Convert to minutes
    }))
    .sort((a, b) => b.duration - a.duration)
    .slice(0, 10)

  return (
    <div className="meeting-detail">
      <div className="meeting-header">
        <h2>{meeting.topic || 'Meeting Details'}</h2>
        <div className="action-buttons">
          <button 
            onClick={(e) => {
              e.preventDefault()
              console.log('Sync button clicked for meeting:', meetingId)
              handleSync()
            }} 
            disabled={syncing} 
            className="sync-button"
          >
            {syncing ? 'Syncing...' : 'Sync Meeting'}
          </button>
        </div>
      </div>

      <div className="meeting-info-grid">
        <div className="info-card">
          <h3>Meeting Information</h3>
          <div className="info-item">
            <span className="info-label">Meeting ID:</span>
            <span className="info-value">{meeting.meeting_id}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Host:</span>
            <span className="info-value">{meeting.host_email || 'N/A'}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Start Time:</span>
            <span className="info-value">{formatDate(meeting.start_time)}</span>
          </div>
          <div className="info-item">
            <span className="info-label">End Time:</span>
            <span className="info-value">{formatDate(meeting.end_time)}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Duration:</span>
            <span className="info-value">{formatDuration(meeting.duration)}</span>
          </div>
        </div>

        <div className="info-card">
          <h3>Statistics</h3>
          {stats && (
            <>
              <div className="info-item">
                <span className="info-label">Total Participants:</span>
                <span className="info-value">{stats.total_participants || 0}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Avg Duration:</span>
                <span className="info-value">{formatDuration(stats.avg_duration)}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Min Duration:</span>
                <span className="info-value">{formatDuration(stats.min_duration)}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Max Duration:</span>
                <span className="info-value">{formatDuration(stats.max_duration)}</span>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="section">
        <div className="section-header">
          <h3>Participants ({participants.length})</h3>
          <button onClick={handleSyncParticipants} disabled={syncing} className="sync-button small">
            Sync
          </button>
        </div>
        {participants.length > 0 ? (
          <div className="participants-table">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Join Time</th>
                  <th>Leave Time</th>
                  <th>Duration</th>
                  <th>Location</th>
                </tr>
              </thead>
              <tbody>
                {participants.map((p) => (
                  <tr key={p.id}>
                    <td>{p.user_name || 'N/A'}</td>
                    <td>{p.user_email || 'N/A'}</td>
                    <td>{formatDate(p.join_time)}</td>
                    <td>{formatDate(p.leave_time)}</td>
                    <td>{formatDuration(p.duration)}</td>
                    <td>{p.location || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="empty">No participants found</p>
        )}

        {chartData.length > 0 && (
          <div className="chart-container">
            <h4>Top Participants by Duration</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="duration" fill="#667eea" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className="section">
        <div className="section-header">
          <h3>Recordings ({recordings.length})</h3>
          <button onClick={handleSyncRecordings} disabled={syncing} className="sync-button small">
            Sync
          </button>
        </div>
        {recordings.length > 0 ? (
          <div className="recordings-list">
            {recordings.map((recording) => (
              <div key={recording.id} className="recording-item">
                <div className="recording-info">
                  <h4>{recording.recording_type || 'Recording'}</h4>
                  <p>Type: {recording.file_type} | Size: {recording.file_size ? `${(recording.file_size / 1024 / 1024).toFixed(2)} MB` : 'N/A'}</p>
                  <p>Status: {recording.status}</p>
                  {recording.play_url && (
                    <a href={recording.play_url} target="_blank" rel="noopener noreferrer" className="play-link">
                      Play Recording
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="empty">No recordings found</p>
        )}
      </div>
    </div>
  )
}

export default MeetingDetail

