#!/usr/bin/env python3
"""
Script to clear all meeting data from the database
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from sqlalchemy import text
from config.database import engine, Base

async def clear_database():
    """Clear all data from database tables"""
    print("🗑️  Clearing database...")
    
    async with engine.begin() as conn:
        # Delete all records from tables (in correct order due to foreign keys)
        print("  - Clearing participants...")
        await conn.execute(text("DELETE FROM participants"))
        
        print("  - Clearing recordings...")
        await conn.execute(text("DELETE FROM recordings"))
        
        print("  - Clearing meetings...")
        await conn.execute(text("DELETE FROM meetings"))
        
        # Note: We keep oauth_tokens so user doesn't need to re-authenticate
        # Uncomment next line if you want to clear tokens too:
        # await conn.execute(text("DELETE FROM oauth_tokens"))
        
        print("  - Resetting auto-increment counters...")
        await conn.execute(text("DELETE FROM sqlite_sequence WHERE name IN ('meetings', 'participants', 'recordings')"))
        
    print("✅ Database cleared successfully!")
    print("\nNote: OAuth tokens are preserved (you won't need to re-authenticate)")
    print("To clear tokens too, edit this script and uncomment the token deletion line.")

if __name__ == "__main__":
    asyncio.run(clear_database())

