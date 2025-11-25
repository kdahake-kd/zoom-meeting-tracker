import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Auth endpoints
export const authAPI = {
  getAuthUrl: () => api.get('/auth/zoom'),
  checkStatus: () => api.get('/auth/status'),
  disconnect: () => api.post('/auth/disconnect'),
}

// Meeting endpoints
export const meetingsAPI = {
  getAll: (limit = 50, offset = 0) => 
    api.get(`/api/meetings?limit=${limit}&offset=${offset}`),
  listFromZoom: (meetingType = 'past') => 
    api.get(`/api/meetings/zoom/list?meeting_type=${meetingType}`),
  getById: (meetingId) => api.get(`/api/meetings/${meetingId}`),
  sync: (meetingId) => api.post(`/api/meetings/${meetingId}/sync`),
  getParticipants: (meetingId) => 
    api.get(`/api/meetings/${meetingId}/participants`),
  syncParticipants: (meetingId) => 
    api.post(`/api/meetings/${meetingId}/participants/sync`),
  getStats: (meetingId) => api.get(`/api/meetings/${meetingId}/stats`),
  getRecordings: (meetingId) => 
    api.get(`/api/meetings/${meetingId}/recordings`),
  syncRecordings: (meetingId) => 
    api.post(`/api/meetings/${meetingId}/recordings/sync`),
  downloadRecording: (meetingId, recordingId) => 
    api.post(`/api/meetings/${meetingId}/recordings/${recordingId}/download`),
}

export default api

