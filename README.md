# Zoom Meeting Tracker

A comprehensive full-stack application to track Zoom meetings, extract participant data, monitor connection durations, and manage recordings. Built with **FastAPI** (Python) backend and **React** frontend.

## 🎯 Features

- ✅ **Participant Tracking**: Track how many participants join your Zoom meetings
- ✅ **Connection Duration**: Monitor how long each participant stays connected
- ✅ **Recording Management**: Download and store meeting recordings
- ✅ **Real-time Sync**: Sync meeting data from Zoom API
- ✅ **Statistics Dashboard**: View meeting analytics and participant statistics
- ✅ **Webhook Support**: Real-time updates via Zoom webhooks (optional)
- ✅ **Modern UI**: Beautiful React frontend with charts and visualizations

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   React     │ ◄─────► │   FastAPI    │ ◄─────► │    Zoom     │
│  Frontend   │  HTTP   │   Backend    │   API   │     API     │
│  (Port 3000)│         │  (Port 8000) │         │             │
└─────────────┘         └──────────────┘         └─────────────┘
                              │
                              ▼
                        ┌─────────────┐
                        │   SQLite    │
                        │  Database   │
                        └─────────────┘
```

## 📋 Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 16+** and **npm** (for frontend)
- **Zoom Account** (free tier works, but some features require paid plan)
- **Zoom App Credentials** (Client ID, Client Secret, Account ID)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd zoomcallproject
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp env.template .env
# Edit .env and add your Zoom credentials

# Create data directory
mkdir -p data

# Start server
python main.py
```

Backend runs on: `http://localhost:8000`

### 3. Frontend Setup

```bash
# Navigate to frontend (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on: `http://localhost:3000`

### 4. Authenticate with Zoom

1. Open `http://localhost:3000`
2. Click **"Connect Zoom"** button
3. Authorize the application
4. You're ready to use the app!

## 🔧 Configuration

### Environment Variables

Create `backend/.env` file:

```env
# Zoom API Credentials (Required)
ZOOM_CLIENT_ID=your_zoom_client_id
ZOOM_CLIENT_SECRET=your_zoom_client_secret
ZOOM_ACCOUNT_ID=your_zoom_account_id

# OAuth Redirect URI (Required)
ZOOM_REDIRECT_URI=http://localhost:8000/auth/zoom/callback

# Server Configuration
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/meetings.db

# Webhook Secret (Optional - for webhooks)
WEBHOOK_SECRET_TOKEN=your_webhook_secret_token

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
```

### Zoom App Setup

1. Go to [Zoom App Marketplace](https://marketplace.zoom.us/)
2. Create an **OAuth** app (or **General App**)
3. Configure:
   - **Redirect URI**: `http://localhost:8000/auth/zoom/callback`
   - **Scopes**: See [Scopes Guide](#required-scopes)
4. Copy credentials to `.env` file

## 📚 API Documentation

### Base URL

```
http://localhost:8000
```

### Authentication Endpoints

#### Get OAuth Authorization URL
```http
GET /auth/zoom
```

**Response:**
```json
{
  "auth_url": "https://zoom.us/oauth/authorize?...",
  "redirect": "https://zoom.us/oauth/authorize?..."
}
```

#### OAuth Callback
```http
GET /auth/zoom/callback?code=AUTHORIZATION_CODE
```

**Response:**
- Redirects to frontend with `?auth=success`

#### Check Authentication Status
```http
GET /auth/status
```

**Response:**
```json
{
  "authenticated": true,
  "message": "Valid access token found"
}
```

#### Disconnect Zoom
```http
POST /auth/disconnect
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully disconnected from Zoom. All tokens removed."
}
```

---

### Meeting Endpoints

#### Get All Synced Meetings
```http
GET /api/meetings?limit=50&offset=0
```

**Query Parameters:**
- `limit` (optional): Number of meetings to return (default: 50, max: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "meetings": [
    {
      "id": 1,
      "meeting_id": "123456789",
      "topic": "Team Meeting",
      "start_time": "2025-11-25T10:00:00",
      "end_time": "2025-11-25T11:00:00",
      "duration": 3600,
      "participant_count": 5,
      "host_email": "host@example.com",
      "created_at": "2025-11-25T10:05:00"
    }
  ],
  "limit": 50,
  "offset": 0
}
```

#### Get Meeting Details
```http
GET /api/meetings/{meeting_id}
```

**Response:**
```json
{
  "id": 1,
  "meeting_id": "123456789",
  "topic": "Team Meeting",
  "start_time": "2025-11-25T10:00:00",
  "end_time": "2025-11-25T11:00:00",
  "duration": 3600,
  "participant_count": 5,
  "host_email": "host@example.com",
  "participants": [
    {
      "id": 1,
      "user_id": "user123",
      "user_name": "John Doe",
      "user_email": "john@example.com",
      "join_time": "2025-11-25T10:05:00",
      "leave_time": "2025-11-25T10:55:00",
      "duration": 3000,
      "device": "Windows",
      "location": "New York, US"
    }
  ]
}
```

#### Sync Meeting from Zoom
```http
POST /api/meetings/{meeting_id}/sync
```

**Description:** Fetches meeting data from Zoom API and stores it in the database.

**Response:**
```json
{
  "success": true,
  "message": "Meeting data synced successfully",
  "meeting": {
    "id": 1,
    "meeting_id": "123456789",
    "topic": "Team Meeting",
    ...
  },
  "participants_count": 5,
  "recordings_count": 2,
  "note": null
}
```

#### List Meetings from Zoom API
```http
GET /api/meetings/zoom/list?meeting_type=past&page_size=30
```

**Query Parameters:**
- `meeting_type` (optional): `past`, `live`, or `upcoming` (default: `past`)
- `page_size` (optional): Number of meetings to return (default: 30, max: 300)

**Response:**
```json
{
  "success": true,
  "meetings": [
    {
      "meeting_id": "123456789",
      "topic": "Team Meeting",
      "start_time": "2025-11-25T10:00:00",
      "duration": 3600,
      "host_email": "host@example.com",
      "type": 2,
      "status": "finished"
    }
  ],
  "total": 1,
  "message": "Found 1 past meetings"
}
```

#### Get Meeting Participants
```http
GET /api/meetings/{meeting_id}/participants
```

**Response:**
```json
{
  "participants": [
    {
      "id": 1,
      "user_id": "user123",
      "user_name": "John Doe",
      "user_email": "john@example.com",
      "join_time": "2025-11-25T10:05:00",
      "leave_time": "2025-11-25T10:55:00",
      "duration": 3000,
      "device": "Windows",
      "ip_address": "192.168.1.1",
      "location": "New York, US"
    }
  ]
}
```

#### Sync Participants
```http
POST /api/meetings/{meeting_id}/participants/sync
```

**Description:** Fetches participant data from Zoom API for a specific meeting.

**Response:**
```json
{
  "success": true,
  "participants": [
    {
      "id": 1,
      "user_id": "user123",
      "user_name": "John Doe",
      "user_email": "john@example.com",
      "join_time": "2025-11-25T10:05:00",
      "leave_time": "2025-11-25T10:55:00",
      "duration": 3000,
      "device": "Windows",
      "location": "New York, US"
    }
  ]
}
```

#### Get Meeting Statistics
```http
GET /api/meetings/{meeting_id}/stats
```

**Response:**
```json
{
  "total_participants": 5,
  "avg_duration": 2850.5,
  "min_duration": 1200,
  "max_duration": 3600,
  "total_duration": 14252
}
```

**Note:** Durations are in seconds.

#### Get Meeting Recordings
```http
GET /api/meetings/{meeting_id}/recordings
```

**Response:**
```json
{
  "recordings": [
    {
      "id": 1,
      "recording_id": "rec123",
      "recording_type": "shared_screen_with_speaker_view",
      "file_size": 52428800,
      "file_type": "MP4",
      "recording_start": "2025-11-25T10:00:00",
      "recording_end": "2025-11-25T11:00:00",
      "file_path": "recordings/123456789/rec123.mp4",
      "status": "downloaded",
      "play_url": "https://zoom.us/rec/play/..."
    }
  ]
}
```

#### Sync Recordings
```http
POST /api/meetings/{meeting_id}/recordings/sync
```

**Description:** Fetches recording information from Zoom API.

**Response:**
```json
{
  "success": true,
  "recordings": [
    {
      "id": 1,
      "recording_id": "rec123",
      "recording_type": "shared_screen_with_speaker_view",
      "file_size": 52428800,
      "file_type": "MP4",
      "status": "pending"
    }
  ]
}
```

#### Download Recording
```http
POST /api/meetings/{meeting_id}/recordings/{recording_id}/download
```

**Description:** Downloads recording file and saves it locally.

**Response:**
```json
{
  "success": true,
  "message": "Recording downloaded successfully",
  "file_path": "recordings/123456789/rec123.mp4"
}
```

---

### Webhook Endpoints

#### Zoom Webhook Handler
```http
POST /webhooks/zoom
```

**Description:** Receives webhook events from Zoom.

**Headers:**
- `x-zoom-signature`: Webhook signature (for verification)
- `x-zoom-request-id`: Unique request ID

**Supported Events:**
- `meeting.started`
- `meeting.ended`
- `meeting.participant_joined`
- `meeting.participant_left`
- `recording.completed`

**Response:**
```json
{
  "status": "success"
}
```

---

## 🔑 Required Scopes

Your Zoom App must have these scopes selected:

1. ✅ `meeting:read:list_past_participants:admin` - Get past meeting participants
2. ✅ `meeting:read:meeting:admin` - View meeting details
3. ✅ `meeting:read:list_meetings:admin` - List user meetings
4. ✅ `recording:read:admin` - Access recordings
5. ✅ `user:read:admin` - Basic user information

**Note:** If `:admin` doesn't work, try `:master` versions.

---

## 📊 Data Models

### Meeting
```python
{
  "id": Integer,
  "meeting_id": String (unique),
  "topic": String,
  "start_time": DateTime,
  "end_time": DateTime,
  "duration": Integer (seconds),
  "participant_count": Integer,
  "host_email": String,
  "created_at": DateTime,
  "updated_at": DateTime
}
```

### Participant
```python
{
  "id": Integer,
  "meeting_id": String (foreign key),
  "user_id": String,
  "user_name": String,
  "user_email": String,
  "join_time": DateTime,
  "leave_time": DateTime,
  "duration": Integer (seconds),
  "device": String,
  "ip_address": String,
  "location": String,
  "created_at": DateTime
}
```

### Recording
```python
{
  "id": Integer,
  "meeting_id": String (foreign key),
  "recording_id": String (unique),
  "recording_type": String,
  "file_size": Integer (bytes),
  "file_type": String,
  "download_url": String,
  "play_url": String,
  "recording_start": DateTime,
  "recording_end": DateTime,
  "file_path": String,
  "status": String,
  "created_at": DateTime
}
```

---

## 🎯 Usage Examples

### Example 1: Sync a Meeting

```bash
# Get meeting ID from Zoom
MEETING_ID="89162351100"

# Sync meeting
curl -X POST http://localhost:8000/api/meetings/$MEETING_ID/sync
```

### Example 2: Get Participant Data

```bash
# Get participants for a meeting
curl http://localhost:8000/api/meetings/$MEETING_ID/participants
```

### Example 3: Get Statistics

```bash
# Get meeting statistics
curl http://localhost:8000/api/meetings/$MEETING_ID/stats
```

### Example 4: List All Meetings from Zoom

```bash
# Get past meetings
curl http://localhost:8000/api/meetings/zoom/list?meeting_type=past

# Get live meetings
curl http://localhost:8000/api/meetings/zoom/list?meeting_type=live

# Get upcoming meetings
curl http://localhost:8000/api/meetings/zoom/list?meeting_type=upcoming
```

---

## 🗂️ Project Structure

```
zoomcallproject/
├── backend/
│   ├── config/
│   │   └── database.py          # Database models and configuration
│   ├── routes/
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── meetings.py          # Meeting endpoints
│   │   └── webhooks.py          # Webhook handlers
│   ├── services/
│   │   ├── zoom_service.py      # Zoom API client
│   │   └── meeting_service.py   # Business logic
│   ├── scripts/
│   │   └── clear_database.py    # Database cleanup utility
│   ├── main.py                  # FastAPI application entry point
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Environment variables (not in git)
│
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   │   └── Navbar.jsx
│   │   ├── pages/               # Page components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── MeetingDetail.jsx
│   │   │   └── Auth.jsx
│   │   ├── services/            # API client
│   │   │   └── api.js
│   │   ├── App.jsx              # Main app component
│   │   └── main.jsx             # Entry point
│   ├── package.json             # Node dependencies
│   └── vite.config.js           # Vite configuration
│
├── README.md                    # This file
└── .gitignore                   # Git ignore rules
```

---

## 🔄 How It Works

### 1. Authentication Flow

```
User → Click "Connect Zoom" 
  → Redirected to Zoom OAuth
  → User authorizes app
  → Zoom redirects with code
  → Backend exchanges code for token
  → Token stored in database
  → User authenticated ✅
```

### 2. Meeting Sync Flow

```
User → Click "Load Past" 
  → Frontend calls GET /api/meetings/zoom/list
  → Backend calls Zoom API
  → Returns list of meetings
  → User clicks "Sync This Meeting"
  → Frontend calls POST /api/meetings/{id}/sync
  → Backend:
    1. Fetches meeting details from Zoom
    2. Stores in database
    3. Fetches participants (if available)
    4. Fetches recordings (if available)
  → Returns success
  → Meeting appears in "Synced Meetings"
```

### 3. Data Extraction

**Participant Data:**
- Join time
- Leave time
- Connection duration (calculated)
- Device information
- Location
- IP address

**Meeting Data:**
- Topic
- Start/end times
- Duration
- Host information
- Participant count

**Statistics:**
- Total participants
- Average connection duration
- Min/Max durations
- Total meeting time

---

## ⚠️ Limitations

### Free Zoom Account

- ❌ **Past meeting participants** - Requires paid account
- ❌ **Detailed reports** - Limited access
- ⚠️ **Cloud recording** - May require paid plan
- ✅ **Meeting basic info** - Works fine
- ✅ **Meeting list** - Works fine

### Paid Zoom Account

- ✅ **Full participant data** - All features available
- ✅ **Connection durations** - Accurate tracking
- ✅ **Cloud recordings** - Full access
- ✅ **Advanced statistics** - Complete analytics

---

## 🧪 Testing

### Test Authentication

```bash
curl http://localhost:8000/auth/status
```

### Test Meeting Sync

```bash
curl -X POST http://localhost:8000/api/meetings/YOUR_MEETING_ID/sync
```

### Test API Health

```bash
curl http://localhost:8000/health
```

---

## 🐛 Troubleshooting

### "Invalid redirect" Error
- **Fix:** Make sure redirect URI in Zoom App matches exactly: `http://localhost:8000/auth/zoom/callback`

### "No meetings found"
- **Fix:** Create a meeting in Zoom first, end it, wait 2-3 minutes, then sync

### "Permission denied"
- **Fix:** Check all required scopes are selected in Zoom App

### "No participants found"
- **Fix:** This is expected for free accounts. Upgrade to paid account for participant data.

---

## 📝 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues or questions:
- Check Zoom API documentation: https://marketplace.zoom.us/docs/api-reference
- Review FastAPI docs: https://fastapi.tiangolo.com/
- Check React docs: https://react.dev/

---

## 🎉 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Frontend with [React](https://react.dev/)
- Charts with [Recharts](https://recharts.org/)
- Database with [SQLAlchemy](https://www.sqlalchemy.org/)

---

**Happy Tracking!** 🚀
