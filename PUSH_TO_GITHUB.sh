#!/bin/bash

# GitHub Push Script for Zoom Meeting Tracker
# Run this script after creating your GitHub repository

echo "🚀 Starting GitHub Push Process..."
echo ""

# Step 1: Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Error: README.md not found. Make sure you're in the project root directory."
    exit 1
fi

# Step 2: Check git status
echo "📋 Checking git status..."
git status

echo ""
echo "⚠️  IMPORTANT: Before proceeding, make sure:"
echo "   1. You've created a GitHub repository"
echo "   2. You have the repository URL ready"
echo "   3. Your .env file is NOT being committed (check .gitignore)"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Step 3: Add all files
echo ""
echo "📦 Adding all files to git..."
git add .

# Step 4: Create initial commit
echo ""
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Zoom Meeting Tracker - Full-stack application for tracking Zoom meetings, participants, and recordings"

# Step 5: Rename branch to main
echo ""
echo "🌿 Renaming branch to main..."
git branch -M main

# Step 6: Add remote (user needs to provide URL)
echo ""
echo "🔗 Adding GitHub remote..."
echo "Please enter your GitHub repository URL:"
echo "Example: https://github.com/yourusername/zoom-meeting-tracker.git"
read -p "Repository URL: " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ Error: Repository URL is required"
    exit 1
fi

# Check if remote already exists
if git remote get-url origin &>/dev/null; then
    echo "⚠️  Remote 'origin' already exists. Removing it..."
    git remote remove origin
fi

git remote add origin "$REPO_URL"

# Step 7: Verify remote
echo ""
echo "✅ Verifying remote..."
git remote -v

# Step 8: Push to GitHub
echo ""
echo "🚀 Pushing to GitHub..."
echo "You may be asked for your GitHub username and password/token"
git push -u origin main

echo ""
echo "✅ Done! Your code should now be on GitHub."
echo "Visit: $REPO_URL"
echo ""
echo "📝 Note: If authentication fails, you may need to:"
echo "   1. Use a Personal Access Token instead of password"
echo "   2. Or set up SSH keys"
echo "   See GITHUB_SETUP.md for details"

