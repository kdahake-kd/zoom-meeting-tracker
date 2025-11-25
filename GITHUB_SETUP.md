# GitHub Setup Guide - Step by Step

## 🚀 Complete Guide to Push Your Project to GitHub

---

## Step 1: Create GitHub Repository

### Option A: Using GitHub Website (Recommended)

1. **Go to GitHub:**
   - Visit: https://github.com
   - Log in to your account

2. **Create New Repository:**
   - Click **"+"** icon (top right) → **"New repository"**
   - **Repository name:** `zoom-meeting-tracker` (or your preferred name)
   - **Description:** "Track Zoom meetings, participants, and recordings"
   - **Visibility:** Choose **Public** or **Private**
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
   - Click **"Create repository"**

3. **Copy Repository URL:**
   - You'll see a page with setup instructions
   - Copy the repository URL (e.g., `https://github.com/yourusername/zoom-meeting-tracker.git`)

---

## Step 2: Initialize Git (If Not Already Done)

### Check if Git is Initialized

```bash
cd /Users/kirandahake/Downloads/zoomcallproject
git status
```

### If Git is NOT Initialized:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Zoom Meeting Tracker application"
```

### If Git IS Already Initialized:

```bash
# Just add and commit any new changes
git add .
git commit -m "Update project files"
```

---

## Step 3: Add GitHub Remote

```bash
# Add your GitHub repository as remote
# Replace YOUR_USERNAME and YOUR_REPO_NAME with your actual values
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Verify remote was added
git remote -v
```

**Example:**
```bash
git remote add origin https://github.com/kirandahake/zoom-meeting-tracker.git
```

---

## Step 4: Push to GitHub

### First Push (Main Branch)

```bash
# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**If you get authentication error:**
- GitHub may ask for username and password
- Use a **Personal Access Token** instead of password
- See "Authentication Setup" below

---

## Step 5: Verify Upload

1. **Go to your GitHub repository:**
   - Visit: `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME`

2. **Verify files are there:**
   - You should see all your project files
   - README.md should be visible
   - All code files should be present

---

## 🔐 Authentication Setup

### If GitHub Asks for Credentials:

#### Option 1: Personal Access Token (Recommended)

1. **Create Token:**
   - Go to: https://github.com/settings/tokens
   - Click **"Generate new token"** → **"Generate new token (classic)"**
   - **Note:** "Zoom Meeting Tracker"
   - **Expiration:** 90 days (or your preference)
   - **Scopes:** Check `repo` (full control of private repositories)
   - Click **"Generate token"**
   - **Copy the token** (you won't see it again!)

2. **Use Token:**
   ```bash
   # When prompted for password, paste the token instead
   git push -u origin main
   # Username: your_github_username
   # Password: paste_your_token_here
   ```

#### Option 2: SSH Key (Alternative)

1. **Generate SSH Key:**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   # Press Enter to accept default location
   # Press Enter for no passphrase (or set one)
   ```

2. **Add to SSH Agent:**
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

3. **Copy Public Key:**
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # Copy the output
   ```

4. **Add to GitHub:**
   - Go to: https://github.com/settings/keys
   - Click **"New SSH key"**
   - **Title:** "My MacBook"
   - **Key:** Paste your public key
   - Click **"Add SSH key"**

5. **Use SSH URL:**
   ```bash
   git remote set-url origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

---

## 📋 Complete Command Sequence

### First Time Setup:

```bash
# 1. Navigate to project
cd /Users/kirandahake/Downloads/zoomcallproject

# 2. Initialize git (if not done)
git init

# 3. Add all files
git add .

# 4. Create initial commit
git commit -m "Initial commit: Zoom Meeting Tracker"

# 5. Add GitHub remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 6. Rename branch to main
git branch -M main

# 7. Push to GitHub
git push -u origin main
```

---

## 🔄 Updating Your Repository

### When You Make Changes:

```bash
# 1. Check what changed
git status

# 2. Add changed files
git add .

# 3. Commit changes
git commit -m "Description of your changes"

# 4. Push to GitHub
git push
```

### Example:

```bash
git add .
git commit -m "Add participant tracking feature"
git push
```

---

## 📁 What Gets Uploaded

### ✅ Files That ARE Uploaded:
- All source code (`.py`, `.jsx`, `.js` files)
- Configuration files (`package.json`, `requirements.txt`)
- Documentation (`README.md`, guides)
- Project structure

### ❌ Files That Are NOT Uploaded (via .gitignore):
- `.env` file (contains secrets)
- `node_modules/` (dependencies)
- `venv/` (Python virtual environment)
- `data/` (database files)
- `recordings/` (downloaded recordings)
- `__pycache__/` (Python cache)

---

## 🛡️ Security Notes

### Important: Never Commit Secrets!

Your `.gitignore` already excludes:
- ✅ `.env` file (Zoom credentials)
- ✅ Database files
- ✅ Recordings

**Before pushing, verify:**
```bash
# Check what will be committed
git status

# Make sure .env is NOT listed
```

**If .env is listed:**
```bash
# Remove it from staging
git reset HEAD .env

# Verify it's in .gitignore
cat .gitignore | grep .env
```

---

## 📝 Repository Settings

### After Creating Repository:

1. **Add Description:**
   - Go to repository settings
   - Add description: "Track Zoom meetings, participants, and recordings"

2. **Add Topics:**
   - Click on gear icon next to "About"
   - Add topics: `zoom`, `fastapi`, `react`, `meeting-tracker`, `api`

3. **Enable GitHub Pages (Optional):**
   - Settings → Pages
   - Source: `main` branch
   - Save

---

## 🔍 Verify Your Upload

### Check Repository:

1. **Visit your repository URL**
2. **Verify files:**
   - ✅ `README.md` is visible
   - ✅ `backend/` folder exists
   - ✅ `frontend/` folder exists
   - ✅ `.gitignore` is present
   - ✅ All code files are there

3. **Check README:**
   - Click on `README.md`
   - Should display nicely formatted

---

## 🎯 Quick Reference Commands

```bash
# Check status
git status

# Add all changes
git add .

# Commit changes
git commit -m "Your commit message"

# Push to GitHub
git push

# Pull latest changes (if working from multiple machines)
git pull

# View commit history
git log

# View remote repositories
git remote -v
```

---

## 🆘 Troubleshooting

### Error: "remote origin already exists"
```bash
# Remove existing remote
git remote remove origin

# Add again
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

### Error: "Authentication failed"
- Use Personal Access Token instead of password
- Or set up SSH keys (see above)

### Error: "Permission denied"
- Check repository URL is correct
- Verify you have write access
- Check authentication method

### Error: "Large files"
```bash
# If you accidentally added large files
git rm --cached large_file.mp4
git commit -m "Remove large file"
git push
```

---

## 📚 Next Steps After Uploading

1. **Add License:**
   - GitHub → Add file → Create new file
   - Name: `LICENSE`
   - Choose a license (MIT recommended)

2. **Add Badges (Optional):**
   - Add to README.md
   - Shows project status

3. **Create Issues:**
   - Track bugs
   - Feature requests

4. **Enable Actions (Optional):**
   - Set up CI/CD
   - Automated testing

---

## ✅ Checklist

Before pushing:
- [ ] `.env` file is NOT in repository (check `.gitignore`)
- [ ] Database files are NOT in repository
- [ ] `node_modules/` is NOT in repository
- [ ] `venv/` is NOT in repository
- [ ] README.md is updated and clear
- [ ] All code is committed
- [ ] GitHub repository is created
- [ ] Remote is added correctly

After pushing:
- [ ] Files are visible on GitHub
- [ ] README displays correctly
- [ ] No sensitive data is exposed
- [ ] Repository is accessible

---

## 🎉 Success!

Once you see your files on GitHub, you're done! 

**Your repository URL will be:**
```
https://github.com/YOUR_USERNAME/YOUR_REPO_NAME
```

Share this URL with others to collaborate or showcase your work!

---

**Happy Coding!** 🚀

