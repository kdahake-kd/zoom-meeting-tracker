from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Optional
from datetime import datetime
import httpx
from config.database import Meeting, Participant, Recording
from services.zoom_service import zoom_service
import os

class MeetingService:
    async def store_meeting(self, db: AsyncSession, meeting_data: Dict) -> Meeting:
        """Store or update meeting data"""
        result = await db.execute(
            select(Meeting).where(Meeting.meeting_id == meeting_data["meeting_id"])
        )
        meeting = result.scalar_one_or_none()

        if meeting:
            # Update existing meeting
            for key, value in meeting_data.items():
                if hasattr(meeting, key):
                    setattr(meeting, key, value)
            meeting.updated_at = datetime.utcnow()
        else:
            # Create new meeting
            meeting = Meeting(**meeting_data)
            db.add(meeting)

        await db.commit()
        await db.refresh(meeting)
        return meeting

    async def store_participant(self, db: AsyncSession, participant_data: Dict) -> Participant:
        """Store or update participant data"""
        # Calculate duration if both join and leave times are available
        if participant_data.get("join_time") and participant_data.get("leave_time"):
            join = participant_data["join_time"]
            leave = participant_data["leave_time"]
            if isinstance(join, str):
                join = datetime.fromisoformat(join.replace("Z", "+00:00"))
            if isinstance(leave, str):
                leave = datetime.fromisoformat(leave.replace("Z", "+00:00"))
            duration = int((leave - join).total_seconds())
            participant_data["duration"] = duration

        result = await db.execute(
            select(Participant).where(
                Participant.meeting_id == participant_data["meeting_id"],
                Participant.user_id == participant_data.get("user_id")
            )
        )
        participant = result.scalar_one_or_none()

        if participant:
            # Update existing participant
            for key, value in participant_data.items():
                if hasattr(participant, key):
                    setattr(participant, key, value)
        else:
            # Create new participant
            participant = Participant(**participant_data)
            db.add(participant)

        await db.commit()
        await db.refresh(participant)
        return participant

    async def sync_meeting_participants(
        self, 
        db: AsyncSession, 
        meeting_id: str
    ) -> List[Participant]:
        """Fetch and store meeting participants from Zoom API"""
        try:
            participants_data = await zoom_service.get_meeting_participants(meeting_id, db)
            participants = []

            if not participants_data:
                print(f"Note: No participant data available for meeting {meeting_id}. This may require a paid Zoom account.")
                return []

            for p_data in participants_data:
                participant_data = {
                    "meeting_id": meeting_id,
                    "user_id": p_data.get("user_id") or p_data.get("id"),
                    "user_name": p_data.get("name") or p_data.get("user_name"),
                    "user_email": p_data.get("user_email") or p_data.get("email"),
                    "join_time": self._parse_datetime(p_data.get("join_time")),
                    "leave_time": self._parse_datetime(p_data.get("leave_time")),
                    "device": p_data.get("device") or (", ".join(p_data.get("devices", [])) if isinstance(p_data.get("devices"), list) else None),
                    "ip_address": p_data.get("ip_address"),
                    "location": p_data.get("location")
                }
                participant = await self.store_participant(db, participant_data)
                participants.append(participant)

            # Update participant count
            await self.update_participant_count(db, meeting_id)

            return participants
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                print(f"Meeting {meeting_id} not found or not accessible. It might be an instant meeting or you may not have permission.")
                return []  # Return empty list instead of raising error
            elif e.response.status_code == 403 or "Paid" in str(e.response.text) or "ZMP" in str(e.response.text):
                print(f"Free account limitation: Past meeting participants require a paid Zoom account.")
                return []  # Return empty list for free accounts
            raise
        except Exception as e:
            print(f"Error syncing participants: {e}")
            raise

    async def update_participant_count(self, db: AsyncSession, meeting_id: str) -> int:
        """Update participant count for a meeting"""
        result = await db.execute(
            select(func.count(Participant.id)).where(Participant.meeting_id == meeting_id)
        )
        count = result.scalar_one()

        result = await db.execute(
            select(Meeting).where(Meeting.meeting_id == meeting_id)
        )
        meeting = result.scalar_one_or_none()

        if meeting:
            meeting.participant_count = count
            meeting.updated_at = datetime.utcnow()
            await db.commit()

        return count

    async def get_meeting_details(
        self, 
        db: AsyncSession, 
        meeting_id: str
    ) -> Optional[Dict]:
        """Get meeting with participants"""
        result = await db.execute(
            select(Meeting).where(Meeting.meeting_id == meeting_id)
        )
        meeting = result.scalar_one_or_none()

        if not meeting:
            return None

        # Get participants
        result = await db.execute(
            select(Participant)
            .where(Participant.meeting_id == meeting_id)
            .order_by(Participant.join_time)
        )
        participants = result.scalars().all()

        return {
            "id": meeting.id,
            "meeting_id": meeting.meeting_id,
            "topic": meeting.topic,
            "start_time": meeting.start_time.isoformat() if meeting.start_time else None,
            "end_time": meeting.end_time.isoformat() if meeting.end_time else None,
            "duration": meeting.duration,
            "participant_count": meeting.participant_count,
            "host_email": meeting.host_email,
            "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
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
                    "ip_address": p.ip_address,
                    "location": p.location
                }
                for p in participants
            ]
        }

    async def get_all_meetings(
        self, 
        db: AsyncSession, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Meeting]:
        """Get all meetings"""
        result = await db.execute(
            select(Meeting)
            .order_by(Meeting.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def get_participant_stats(
        self, 
        db: AsyncSession, 
        meeting_id: str
    ) -> Dict:
        """Get participant statistics"""
        result = await db.execute(
            select(
                func.count(Participant.id).label("total_participants"),
                func.avg(Participant.duration).label("avg_duration"),
                func.min(Participant.duration).label("min_duration"),
                func.max(Participant.duration).label("max_duration"),
                func.sum(Participant.duration).label("total_duration")
            ).where(
                Participant.meeting_id == meeting_id,
                Participant.duration.isnot(None)
            )
        )
        stats = result.first()
        return {
            "total_participants": stats.total_participants or 0,
            "avg_duration": float(stats.avg_duration) if stats.avg_duration else 0,
            "min_duration": stats.min_duration or 0,
            "max_duration": stats.max_duration or 0,
            "total_duration": stats.total_duration or 0
        }

    async def store_recording(self, db: AsyncSession, recording_data: Dict) -> Recording:
        """Store recording information"""
        result = await db.execute(
            select(Recording).where(Recording.recording_id == recording_data["recording_id"])
        )
        recording = result.scalar_one_or_none()

        if recording:
            # Update existing recording
            for key, value in recording_data.items():
                if hasattr(recording, key):
                    setattr(recording, key, value)
        else:
            # Create new recording
            recording = Recording(**recording_data)
            db.add(recording)

        await db.commit()
        await db.refresh(recording)
        return recording

    async def sync_meeting_recordings(
        self, 
        db: AsyncSession, 
        meeting_id: str
    ) -> List[Recording]:
        """Fetch and store recordings from Zoom API"""
        recordings_data = await zoom_service.get_meeting_recordings(meeting_id, db)
        recordings = []

        for r_data in recordings_data:
            recording_data = {
                "meeting_id": meeting_id,
                "recording_id": r_data.get("id"),
                "recording_type": r_data.get("recording_type"),
                "file_size": r_data.get("file_size"),
                "file_type": r_data.get("file_type"),
                "download_url": r_data.get("download_url"),
                "play_url": r_data.get("play_url"),
                "recording_start": self._parse_datetime(r_data.get("recording_start")),
                "recording_end": self._parse_datetime(r_data.get("recording_end")),
                "file_path": None,
                "status": "pending"
            }
            recording = await self.store_recording(db, recording_data)
            recordings.append(recording)

        return recordings

    async def download_recording(
        self, 
        db: AsyncSession, 
        meeting_id: str, 
        recording_id: str
    ) -> str:
        """Download and store recording file"""
        result = await db.execute(
            select(Recording).where(
                Recording.meeting_id == meeting_id,
                Recording.recording_id == recording_id
            )
        )
        recording = result.scalar_one_or_none()

        if not recording or not recording.download_url:
            raise Exception("Recording not found or download URL not available")

        # Create file path
        recordings_dir = os.path.join("recordings", meeting_id)
        os.makedirs(recordings_dir, exist_ok=True)

        file_extension = {
            "MP4": "mp4",
            "M4A": "m4a"
        }.get(recording.file_type, "txt")

        file_path = os.path.join(recordings_dir, f"{recording_id}.{file_extension}")

        # Download the file
        await zoom_service.download_recording(recording.download_url, file_path, db)

        # Update database
        recording.file_path = file_path
        recording.status = "downloaded"
        await db.commit()

        return file_path

    async def get_meeting_recordings(
        self, 
        db: AsyncSession, 
        meeting_id: str
    ) -> List[Recording]:
        """Get all recordings for a meeting"""
        result = await db.execute(
            select(Recording)
            .where(Recording.meeting_id == meeting_id)
            .order_by(Recording.recording_start)
        )
        return result.scalars().all()

    def _parse_datetime(self, dt_string: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object"""
        if not dt_string:
            return None
        try:
            return datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
        except:
            return None


# Singleton instance
meeting_service = MeetingService()

