from fastapi import APIRouter, Request, HTTPException, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from services.meeting_service import meeting_service
from services.zoom_service import zoom_service
import hmac
import hashlib
import os
import json

router = APIRouter()

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature from Zoom"""
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"v0={expected_signature}", signature)

@router.post("/zoom")
async def zoom_webhook(
    request: Request,
    x_zoom_request_id: str = Header(None),
    x_zoom_request_origin: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Handle Zoom webhook events"""
    try:
        body = await request.body()
        payload = await request.json()
        
        # Verify webhook signature (optional but recommended)
        webhook_secret = os.getenv("WEBHOOK_SECRET_TOKEN")
        if webhook_secret:
            signature = request.headers.get("x-zoom-signature", "")
            if not verify_webhook_signature(body, signature, webhook_secret):
                raise HTTPException(status_code=401, detail="Invalid webhook signature")

        event = payload.get("event")
        event_data = payload.get("payload", {}).get("object", {})

        # Handle different webhook events
        if event == "meeting.started":
            await handle_meeting_started(event_data, db)
        elif event == "meeting.ended":
            await handle_meeting_ended(event_data, db)
        elif event == "meeting.participant_joined":
            await handle_participant_joined(event_data, db)
        elif event == "meeting.participant_left":
            await handle_participant_left(event_data, db)
        elif event == "recording.completed":
            await handle_recording_completed(event_data, db)

        return {"status": "success"}
    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def handle_meeting_started(event_data: dict, db: AsyncSession):
    """Handle meeting started event"""
    meeting_id = event_data.get("id")
    if meeting_id:
        meeting_data = {
            "meeting_id": str(meeting_id),
            "topic": event_data.get("topic"),
            "start_time": event_data.get("start_time"),
            "host_email": event_data.get("host", {}).get("email")
        }
        await meeting_service.store_meeting(db, meeting_data)

async def handle_meeting_ended(event_data: dict, db: AsyncSession):
    """Handle meeting ended event"""
    meeting_id = event_data.get("id")
    if meeting_id:
        # Sync participants and recordings
        await meeting_service.sync_meeting_participants(db, str(meeting_id))
        await meeting_service.sync_meeting_recordings(db, str(meeting_id))
        
        # Update meeting end time
        meeting_data = {
            "meeting_id": str(meeting_id),
            "end_time": event_data.get("end_time")
        }
        await meeting_service.store_meeting(db, meeting_data)

async def handle_participant_joined(event_data: dict, db: AsyncSession):
    """Handle participant joined event"""
    meeting_id = event_data.get("id")
    participant = event_data.get("participant", {})
    
    if meeting_id and participant:
        participant_data = {
            "meeting_id": str(meeting_id),
            "user_id": participant.get("user_id"),
            "user_name": participant.get("user_name"),
            "user_email": participant.get("email"),
            "join_time": event_data.get("join_time"),
            "ip_address": participant.get("ip_address"),
            "location": participant.get("location")
        }
        await meeting_service.store_participant(db, participant_data)

async def handle_participant_left(event_data: dict, db: AsyncSession):
    """Handle participant left event"""
    meeting_id = event_data.get("id")
    participant = event_data.get("participant", {})
    
    if meeting_id and participant:
        participant_data = {
            "meeting_id": str(meeting_id),
            "user_id": participant.get("user_id"),
            "leave_time": event_data.get("leave_time")
        }
        await meeting_service.store_participant(db, participant_data)

async def handle_recording_completed(event_data: dict, db: AsyncSession):
    """Handle recording completed event"""
    meeting_id = event_data.get("id")
    if meeting_id:
        await meeting_service.sync_meeting_recordings(db, str(meeting_id))

