# Railway Setup - Step by Step

## IMPORTANT: This is a Monorepo

Railway needs to deploy **3 separate services** from this repository:
1. PostgreSQL Database
2. Backend (from `/backend` directory)
3. Frontend (from `/frontend` directory)

## Step-by-Step Setup

### Step 1: Create a New Project

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your repository
4. Railway will try to auto-deploy - **this will fail** (that's okay!)
5. You should now have an empty project

### Step 2: Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway provisions the database (this takes ~30 seconds)
4. Done! The `DATABASE_URL` environment variable is automatically created

### Step 3: Add Backend Service

1. In your Railway project, click **"+ New"**
2. Select **"GitHub Repo"**
3. Choose your repository again
4. Railway will show service configuration:

**CRITICAL SETTINGS:**
- Click **"Settings"** (gear icon)
- Scroll to **"Root Directory"**
- Set it to: `backend`
- Click **"Deploy"**

5. Add environment variables (Settings → Variables):
   ```
   SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">
   BASE_CURRENCY=MYR
   DEBUG=false
   ```

6. The backend should now build successfully!
7. **Copy the backend URL** (shown in the service overview) - you'll need it for the frontend

### Step 4: Add Frontend Service

1. In your Railway project, click **"+ New"**
2. Select **"GitHub Repo"**
3. Choose your repository again
4. Railway will show service configuration:

**CRITICAL SETTINGS:**
- Click **"Settings"** (gear icon)
- Scroll to **"Root Directory"**
- Set it to: `frontend`
- Click **"Deploy"**

5. Add environment variables (Settings → Variables):
   ```
   API_BASE_URL=<paste backend URL from step 3>
   SECRET_KEY=<same as backend>
   FLASK_ENV=production
   DEBUG=false
   ```

6. The frontend should now build successfully!

### Step 5: Initialize Database

1. Go to the **PostgreSQL service** in Railway
2. Click **"Data"** tab
3. Click **"Query"**
4. Copy the contents of `database/init.sql` and paste it
5. Click **"Run"**

Alternatively, use Railway CLI:
```bash
railway login
railway link
railway connect postgres
# Then paste the SQL from database/init.sql
```

### Step 6: Verify Everything Works

1. Click on the **Frontend service**
2. Find the **public URL** (looks like: `finn-frontend.up.railway.app`)
3. Click to open
4. Your app should be running!

5. Test the backend API:
   - Go to: `<backend-url>/docs`
   - You should see FastAPI documentation

## Troubleshooting

### "Railpack could not determine how to build"
**Solution**: You didn't set the Root Directory. Go to Settings → Root Directory → Set to `backend` or `frontend`

### Backend builds but crashes
**Solution**: Check environment variables are set, especially `DATABASE_URL`

### Frontend can't reach backend
**Solution**: Verify `API_BASE_URL` in frontend points to the correct backend URL

### Database connection error
**Solution**: Make sure PostgreSQL service is running and `DATABASE_URL` is available to backend

## Your Project Structure

```
Railway Project: Finn-The-Humann
├── PostgreSQL (database)
├── finn-backend (root dir: backend/)
└── finn-frontend (root dir: frontend/)
```

## Quick Reference: Root Directories

When adding a service from the repo:
- **Backend service** → Root Directory: `backend`
- **Frontend service** → Root Directory: `frontend`
- **Database** → Use Railway's PostgreSQL plugin (no repo needed)

## Environment Variables Reference

### Backend Service
```env
DATABASE_URL=<auto-set by Railway PostgreSQL>
SECRET_KEY=<generate random string>
BASE_CURRENCY=MYR
DEBUG=false
PORT=<auto-set by Railway>
```

### Frontend Service
```env
API_BASE_URL=https://<your-backend>.up.railway.app
SECRET_KEY=<same as backend>
FLASK_ENV=production
DEBUG=false
PORT=<auto-set by Railway>
```

## Generate SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and use it for both backend and frontend.
