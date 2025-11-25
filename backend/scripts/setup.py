#!/usr/bin/env python3
"""
Setup script to initialize the database and verify configuration
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

def check_env_vars():
    """Check if required environment variables are set"""
    required_vars = [
        'ZOOM_CLIENT_ID',
        'ZOOM_CLIENT_SECRET',
        'ZOOM_ACCOUNT_ID',
        'ZOOM_REDIRECT_URI'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease set these in your .env file")
        return False
    
    print("✅ All required environment variables are set")
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        'data',
        'recordings'
    ]
    
    for dir_name in directories:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_name}")

async def init_database():
    """Initialize database tables"""
    try:
        from config.database import init_db
        await init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

async def main():
    """Main setup function"""
    print("🚀 Setting up Zoom Meeting Tracker...\n")
    
    # Check environment variables
    if not check_env_vars():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Initialize database
    import asyncio
    await init_database()
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Start the backend: python main.py")
    print("2. Start the frontend: cd ../frontend && npm run dev")
    print("3. Open http://localhost:3000 and authenticate with Zoom")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

