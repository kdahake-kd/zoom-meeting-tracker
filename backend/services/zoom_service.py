import httpx
import os
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config.database import OAuthToken
import asyncio

class ZoomService:
    def __init__(self):
        self.base_url = "https://api.zoom.us/v2"
        self.account_id = os.getenv("ZOOM_ACCOUNT_ID")
        self.client_id = os.getenv("ZOOM_CLIENT_ID")
        self.client_secret = os.getenv("ZOOM_CLIENT_SECRET")
        self.redirect_uri = os.getenv("ZOOM_REDIRECT_URI")

    async def get_access_token(self, db: AsyncSession) -> Optional[str]:
        """Get access token from database, refresh if expired"""
        result = await db.execute(
            select(OAuthToken).order_by(OAuthToken.created_at.desc()).limit(1)
        )
        token_record = result.scalar_one_or_none()

        if not token_record:
            raise Exception("No access token found. Please authenticate first.")

        # Check if token is expired
        if token_record.expires_at and datetime.utcnow() >= token_record.expires_at:
            # Token expired, refresh it
            new_token = await self.refresh_access_token(db, token_record.refresh_token)
            return new_token

        return token_record.access_token

    async def refresh_access_token(self, db: AsyncSession, refresh_token: Optional[str]) -> str:
        """Refresh access token using refresh token"""
        if not refresh_token:
            raise Exception("No refresh token found. Please re-authenticate.")

        auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://zoom.us/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token
                },
                headers={
                    "Authorization": f"Basic {auth}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            response.raise_for_status()
            data = response.json()

            # Update token in database
            result = await db.execute(
                select(OAuthToken).order_by(OAuthToken.created_at.desc()).limit(1)
            )
            token_record = result.scalar_one_or_none()

            if token_record:
                expires_at = datetime.utcnow() + timedelta(seconds=data["expires_in"])
                token_record.access_token = data["access_token"]
                token_record.refresh_token = data.get("refresh_token", refresh_token)
                token_record.expires_at = expires_at
            else:
                expires_at = datetime.utcnow() + timedelta(seconds=data["expires_in"])
                token_record = OAuthToken(
                    access_token=data["access_token"],
                    refresh_token=data.get("refresh_token", refresh_token),
                    expires_at=expires_at
                )
                db.add(token_record)

            await db.commit()
            return data["access_token"]

    async def make_request(
        self, 
        method: str, 
        endpoint: str, 
        db: AsyncSession,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Make authenticated API request to Zoom"""
        access_token = await self.get_access_token(db)

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.base_url}{endpoint}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json=data,
                params=params
            )
            if response.status_code != 200:
                error_msg = f"Zoom API Error ({response.status_code})"
                try:
                    error_body = response.json()
                    error_msg = error_body.get("message", error_body.get("error", str(error_body)))
                except:
                    error_msg = response.text or error_msg
                print(f"Zoom API request failed: {method} {endpoint} - {error_msg}")
            response.raise_for_status()
            return response.json()

    async def get_meeting_details(self, meeting_id: str, db: AsyncSession) -> Dict:
        """Get meeting details"""
        return await self.make_request("GET", f"/meetings/{meeting_id}", db)

    async def get_meeting_participants(self, meeting_id: str, db: AsyncSession) -> List[Dict]:
        """Get past meeting participants"""
        try:
            response = await self.make_request(
                "GET", 
                f"/past_meetings/{meeting_id}/participants", 
                db
            )
            return response.get("participants", [])
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Meeting might still be ongoing, try to get live participants
                try:
                    response = await self.make_request("GET", f"/meetings/{meeting_id}", db)
                    return response.get("participants", [])
                except:
                    return []
            elif e.response.status_code == 403 or "Paid" in str(e.response.text) or "ZMP" in str(e.response.text):
                # Free account limitation - past meeting participants require paid account
                print(f"Note: Past meeting participants require a paid Zoom account. Meeting ID: {meeting_id}")
                # Try to get meeting report instead (might work for some data)
                try:
                    report = await self.get_meeting_report(meeting_id, db)
                    if report and report.get("participants"):
                        return report.get("participants", [])
                except:
                    pass
                # Return empty list with a note
                return []
            raise

    async def get_meeting_report(self, meeting_id: str, db: AsyncSession) -> Optional[Dict]:
        """Get meeting report"""
        try:
            return await self.make_request("GET", f"/report/meetings/{meeting_id}", db)
        except Exception as e:
            print(f"Error getting meeting report: {e}")
            return None

    async def get_meeting_recordings(self, meeting_id: str, db: AsyncSession) -> List[Dict]:
        """Get meeting recordings"""
        try:
            response = await self.make_request(
                "GET", 
                f"/meetings/{meeting_id}/recordings", 
                db
            )
            return response.get("recording_files", [])
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                print("No recordings found for this meeting")
                return []
            raise

    async def download_recording(
        self, 
        download_url: str, 
        file_path: str, 
        db: AsyncSession
    ) -> str:
        """Download recording file"""
        import aiofiles
        import os

        access_token = await self.get_access_token(db)

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "GET",
                download_url,
                headers={"Authorization": f"Bearer {access_token}"}
            ) as response:
                response.raise_for_status()
                async with aiofiles.open(file_path, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        await f.write(chunk)

        return file_path

    async def list_meetings(
        self, 
        user_id: str = "me", 
        meeting_type: str = "past",
        db: AsyncSession = None,
        page_size: int = 30
    ) -> Dict:
        """List all meetings"""
        if db is None:
            raise ValueError("Database session is required")
        return await self.make_request(
            "GET", 
            f"/users/{user_id}/meetings",
            db,
            params={"type": meeting_type, "page_size": page_size}
        )


# Singleton instance
zoom_service = ZoomService()

