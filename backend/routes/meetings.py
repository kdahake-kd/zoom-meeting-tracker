from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import httpx
from config.database import get_db
from services.meeting_service import meeting_service
from services.zoom_service import zoom_service

router = APIRouter()

@router.get("/")
async def get_all_meetings(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get all stored meetings"""
    meetings = await meeting_service.get_all_meetings(db, limit, offset)
    return {
        "meetings": [
            {
                "id": m.id,
                "meeting_id": m.meeting_id,
                "topic": m.topic,
                "start_time": m.start_time.isoformat() if m.start_time else None,
                "end_time": m.end_time.isoformat() if m.end_time else None,
                "duration": m.duration,
                "participant_count": m.participant_count,
                "host_email": m.host_email,
                "created_at": m.created_at.isoformat() if m.created_at else None
            }
            for m in meetings
        ],
        "limit": limit,
        "offset": offset
    }

@router.get("/zoom/list")
async def list_zoom_meetings(
    meeting_type: str = Query("past", regex="^(past|live|upcoming)$"),
    page_size: int = Query(30, ge=1, le=300),
    db: AsyncSession = Depends(get_db)
):
    """List meetings from Zoom API"""
    try:
        # Add pagination parameters
        meetings_data = await zoom_service.list_meetings("me", meeting_type, db, page_size=page_size)
        meetings = meetings_data.get("meetings", [])
        
        # Handle case where meetings might be None or empty
        if not meetings:
            meetings = []
        
        return {
            "success": True,
            "meetings": [
                {
                    "meeting_id": str(m.get("id", "")),
                    "topic": m.get("topic", "Untitled Meeting"),
                    "start_time": m.get("start_time"),
                    "duration": m.get("duration", 0),
                    "host_email": m.get("host_email"),
                    "type": m.get("type"),
                    "status": m.get("status")
                }
                for m in meetings
            ],
            "total": len(meetings),
            "message": f"Found {len(meetings)} {meeting_type} meetings" if meetings else f"No {meeting_type} meetings found"
        }
    except httpx.HTTPStatusError as e:
        error_detail = f"Zoom API Error: {e.response.status_code}"
        if e.response.status_code == 404:
            error_detail = "No meetings found. Make sure you have meetings in your Zoom account and the meeting_type is correct (past/live/upcoming)."
        elif e.response.status_code == 403:
            error_detail = "Permission denied. Check your scopes - you need 'meeting:read:list_meetings:admin' scope."
        else:
            try:
                error_body = e.response.json()
                error_detail = f"Zoom API Error ({e.response.status_code}): {error_body.get('message', error_body.get('error', str(error_body)))}"
            except:
                error_detail = f"Zoom API Error ({e.response.status_code}): {e.response.text[:200]}"
        print(f"Error listing meetings: {error_detail}")
        raise HTTPException(status_code=e.response.status_code, detail=error_detail)
    except Exception as e:
        error_msg = str(e)
        print(f"Exception listing meetings: {error_msg}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error listing meetings: {error_msg}")

@router.get("/{meeting_id}")
async def get_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get meeting details with participants"""
    meeting = await meeting_service.get_meeting_details(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@router.post("/{meeting_id}/sync")
async def sync_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Sync meeting data from Zoom API"""
    try:
        # Get meeting details from Zoom
        meeting_data = await zoom_service.get_meeting_details(meeting_id, db)
        
        # Store meeting
        stored_meeting = await meeting_service.store_meeting(db, {
            "meeting_id": meeting_id,
            "topic": meeting_data.get("topic"),
            "start_time": meeting_data.get("start_time"),
            "host_email": meeting_data.get("host_email")
        })

        # Sync participants
        participants = await meeting_service.sync_meeting_participants(db, meeting_id)

        # Sync recordings
        recordings = await meeting_service.sync_meeting_recordings(db, meeting_id)

        message = "Meeting data synced successfully"
        if len(participants) == 0:
            message += ". Note: Participant data requires a paid Zoom account for past meetings."

        # Return meeting data in a format frontend can use
        return {
            "success": True,
            "message": message,
            "meeting": {
                "id": stored_meeting.id,
                "meeting_id": stored_meeting.meeting_id,
                "topic": stored_meeting.topic,
                "start_time": stored_meeting.start_time.isoformat() if stored_meeting.start_time else None,
                "end_time": stored_meeting.end_time.isoformat() if stored_meeting.end_time else None,
                "duration": stored_meeting.duration,
                "participant_count": stored_meeting.participant_count,
                "host_email": stored_meeting.host_email,
                "created_at": stored_meeting.created_at.isoformat() if stored_meeting.created_at else None
            },
            "participants_count": len(participants),
            "recordings_count": len(recordings),
            "note": "Participant data may be limited on free Zoom accounts" if len(participants) == 0 else None
        }
    except httpx.HTTPStatusError as e:
        error_detail = f"Zoom API Error: {e.response.status_code}"
        if e.response.status_code == 404:
            error_detail = f"Meeting {meeting_id} not found. Make sure the meeting exists and you have access to it."
        elif e.response.status_code == 403:
            error_detail = "Permission denied. Check your scopes and make sure you have access to this meeting."
        else:
            try:
                error_body = e.response.json()
                error_detail = f"Zoom API Error ({e.response.status_code}): {error_body.get('message', str(error_body))}"
            except:
                error_detail = f"Zoom API Error ({e.response.status_code}): {e.response.text}"
        print(f"Sync error: {error_detail}")
        raise HTTPException(status_code=e.response.status_code, detail=error_detail)
    except Exception as e:
        error_msg = str(e)
        print(f"Sync error: {error_msg}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {error_msg}")

@router.get("/{meeting_id}/participants")
async def get_meeting_participants(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get participants for a meeting"""
    meeting = await meeting_service.get_meeting_details(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return {"participants": meeting.get("participants", [])}

@router.post("/{meeting_id}/participants/sync")
async def sync_participants(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Sync participants from Zoom API"""
    try:
        participants = await meeting_service.sync_meeting_participants(db, meeting_id)
        return {
            "success": True,
            "participants": [
                {
                    "id": p.id,
                    "user_id": p.user_id,
                    "user_name": p.user_name,
                    "user_email": p.user_email,
                    "join_time": p.join_time.isoformat() if p.join_time else None,
                    "leave_time": p.leave_time.isoformat() if p.leave_time else None,
                    "duration": p.duration,
                    "device": p.device,
                    "location": p.location
                }
                for p in participants
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{meeting_id}/stats")
async def get_meeting_stats(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get meeting statistics"""
    stats = await meeting_service.get_participant_stats(db, meeting_id)
    return stats

@router.get("/{meeting_id}/recordings")
async def get_meeting_recordings(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get recordings for a meeting"""
    recordings = await meeting_service.get_meeting_recordings(db, meeting_id)
    return {
        "recordings": [
            {
                "id": r.id,
                "recording_id": r.recording_id,
                "recording_type": r.recording_type,
                "file_size": r.file_size,
                "file_type": r.file_type,
                "recording_start": r.recording_start.isoformat() if r.recording_start else None,
                "recording_end": r.recording_end.isoformat() if r.recording_end else None,
                "file_path": r.file_path,
                "status": r.status,
                "play_url": r.play_url
            }
            for r in recordings
        ]
    }

@router.post("/{meeting_id}/recordings/sync")
async def sync_recordings(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Sync recordings from Zoom API"""
    try:
        recordings = await meeting_service.sync_meeting_recordings(db, meeting_id)
        return {
            "success": True,
            "recordings": [
                {
                    "id": r.id,
                    "recording_id": r.recording_id,
                    "recording_type": r.recording_type,
                    "file_size": r.file_size,
                    "file_type": r.file_type,
                    "status": r.status
                }
                for r in recordings
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{meeting_id}/recordings/{recording_id}/download")
async def download_recording(
    meeting_id: str,
    recording_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Download recording file"""
    try:
        file_path = await meeting_service.download_recording(db, meeting_id, recording_id)
        return {
            "success": True,
            "message": "Recording downloaded successfully",
            "file_path": file_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

