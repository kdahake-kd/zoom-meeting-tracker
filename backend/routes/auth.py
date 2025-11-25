from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
import os
import base64
from datetime import datetime, timedelta
from config.database import get_db, OAuthToken

router = APIRouter()

@router.get("/zoom")
async def initiate_oauth():
    """Step 1: Redirect user to Zoom OAuth"""
    client_id = os.getenv("ZOOM_CLIENT_ID")
    redirect_uri = os.getenv("ZOOM_REDIRECT_URI")
    
    if not client_id or not redirect_uri:
        raise HTTPException(
            status_code=500,
            detail="Zoom OAuth credentials not configured"
        )
    
    zoom_auth_url = (
        f"https://zoom.us/oauth/authorize?"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}"
    )
    
    return {"auth_url": zoom_auth_url, "redirect": zoom_auth_url}

@router.get("/zoom/callback")
async def oauth_callback(
    code: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Step 2: Handle OAuth callback and store tokens"""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")

    client_id = os.getenv("ZOOM_CLIENT_ID")
    client_secret = os.getenv("ZOOM_CLIENT_SECRET")
    redirect_uri = os.getenv("ZOOM_REDIRECT_URI")

    if not all([client_id, client_secret, redirect_uri]):
        raise HTTPException(
            status_code=500,
            detail="Zoom OAuth credentials not configured"
        )

    try:
        # Exchange authorization code for access token
        auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://zoom.us/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri
                },
                headers={
                    "Authorization": f"Basic {auth}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            response.raise_for_status()
            data = response.json()

        # Store tokens in database
        expires_at = datetime.utcnow() + timedelta(seconds=data["expires_in"])
        token_record = OAuthToken(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_at=expires_at
        )
        db.add(token_record)
        await db.commit()

        # Redirect to frontend with success
        from fastapi.responses import RedirectResponse
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(url=f"{frontend_url}/?auth=success")
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to authenticate with Zoom: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def auth_status(db: AsyncSession = Depends(get_db)):
    """Check authentication status"""
    try:
        from services.zoom_service import zoom_service
        token = await zoom_service.get_access_token(db)
        return {
            "authenticated": True,
            "message": "Valid access token found"
        }
    except Exception as e:
        return {
            "authenticated": False,
            "message": "No valid access token. Please authenticate at /auth/zoom"
        }

@router.post("/disconnect")
async def disconnect_zoom(db: AsyncSession = Depends(get_db)):
    """Disconnect Zoom - Remove OAuth tokens"""
    try:
        from sqlalchemy import delete
        from config.database import OAuthToken
        
        # Delete all OAuth tokens
        await db.execute(delete(OAuthToken))
        await db.commit()
        
        return {
            "success": True,
            "message": "Successfully disconnected from Zoom. All tokens removed."
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error disconnecting: {str(e)}")

