# Railway.app Deployment Guide

This guide explains how to deploy the Finn-The-Humann financial tracking application on Railway.app.

## Architecture Overview

The application consists of three services:
1. **PostgreSQL Database** - Railway PostgreSQL plugin
2. **FastAPI Backend** - API server (backend/)
3. **Flask Frontend** - Web interface (frontend/)

## Prerequisites

- Railway.app account (sign up at https://railway.app)
- GitHub repository connected to Railway
- Railway CLI (optional, for local testing)

## Deployment Steps

### 1. Create a New Project on Railway

1. Go to https://railway.app/new
2. Select "Deploy from GitHub repo"
3. Choose your `Finn-The-Humann-App` repository
4. Railway will create a new project

### 2. Add PostgreSQL Database

1. In your Railway project dashboard, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway will provision a PostgreSQL instance
4. Note: Railway automatically creates a `DATABASE_URL` environment variable

### 3. Deploy Backend Service

1. In your Railway project, click "+ New" → "GitHub Repo"
2. Select the repository again
3. Railway will ask which service to deploy
4. Configure the service:
   - **Name**: `finn-backend`
   - **Root Directory**: `backend`
   - **Builder**: Docker (detected automatically from Dockerfile)
5. Railway will use `backend/railway.toml` for configuration

#### Backend Environment Variables

Add these environment variables to the backend service:

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | (auto-set by Railway) | PostgreSQL connection string |
| `SECRET_KEY` | (generate random string) | Application secret key |
| `BASE_CURRENCY` | `MYR` | Default currency |
| `DEBUG` | `false` | Disable debug mode |
| `PORT` | (auto-set by Railway) | Port for the service |

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Deploy Frontend Service

1. In your Railway project, click "+ New" → "GitHub Repo"
2. Select the repository again
3. Configure the service:
   - **Name**: `finn-frontend`
   - **Root Directory**: `frontend`
   - **Builder**: Docker (detected automatically)
4. Railway will use `frontend/railway.toml` for configuration

#### Frontend Environment Variables

Add these environment variables to the frontend service:

| Variable | Value | Description |
|----------|-------|-------------|
| `API_BASE_URL` | (see below) | Backend API URL |
| `SECRET_KEY` | (same as backend) | Application secret key |
| `FLASK_ENV` | `production` | Flask environment |
| `DEBUG` | `false` | Disable debug mode |
| `PORT` | (auto-set by Railway) | Port for the service |

**Setting API_BASE_URL:**
1. Go to your `finn-backend` service settings
2. Copy the service URL (e.g., `https://finn-backend-production.up.railway.app`)
3. Set as `API_BASE_URL` in the frontend service

### 5. Initialize Database Schema

After the backend is deployed:

1. Go to the PostgreSQL service in Railway
2. Click "Connect" → "Connect via psql" or use the Query tab
3. Run the initialization script:

```sql
-- Copy and paste the contents of database/init.sql here
```

Alternatively, connect using Railway CLI:
```bash
railway connect postgres
\i database/init.sql
```

### 6. Verify Deployment

1. Open the frontend URL (from Railway dashboard)
2. Check that the application loads
3. Verify API connectivity:
   - Visit `<backend-url>/docs` for API documentation
   - Test creating an account and asset

## Service Configuration Files

### Backend (backend/railway.toml)
```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
healthcheckPath = "/docs"
healthcheckTimeout = 100
```

### Frontend (frontend/railway.toml)
```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "gunicorn -w 4 -b 0.0.0.0:$PORT 'app:create_app()'"
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
healthcheckPath = "/"
healthcheckTimeout = 100
```

## Environment Variable Summary

### Backend Service
```env
DATABASE_URL=postgresql://user:pass@host:port/dbname  # Auto-set by Railway
SECRET_KEY=your-secret-key-here
BASE_CURRENCY=MYR
DEBUG=false
PORT=8000  # Auto-set by Railway
```

### Frontend Service
```env
API_BASE_URL=https://finn-backend-production.up.railway.app
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
DEBUG=false
PORT=5000  # Auto-set by Railway
```

## Monitoring and Logs

### View Logs
1. Go to Railway dashboard
2. Click on the service (backend or frontend)
3. Navigate to "Deployments" tab
4. Click on the active deployment
5. View real-time logs

### Service Metrics
Railway provides:
- CPU usage
- Memory usage
- Network traffic
- Deployment history

## Troubleshooting

### Backend can't connect to database
- Ensure PostgreSQL service is running
- Check `DATABASE_URL` is set correctly
- Verify database schema is initialized

### Frontend can't reach backend
- Verify `API_BASE_URL` points to correct backend URL
- Check backend service is running
- Test backend API at `<backend-url>/docs`

### Build failures
- Check Dockerfile syntax
- Verify requirements.txt dependencies
- Review build logs in Railway dashboard

### Application crashes on startup
- Check environment variables are set
- Review service logs
- Ensure `PORT` variable is used correctly

## Custom Domain (Optional)

To add a custom domain:

1. Go to service settings in Railway
2. Click "Networking" → "Custom Domain"
3. Add your domain (e.g., `app.yourdomain.com`)
4. Update DNS records as instructed by Railway
5. Railway automatically provisions SSL certificate

## Costs

Railway pricing (as of 2024):
- **Hobby Plan**: $5/month + usage
- **Pro Plan**: $20/month + usage

Estimated costs for this app:
- PostgreSQL: ~$5-10/month
- Backend service: ~$5/month
- Frontend service: ~$5/month
- **Total**: ~$15-20/month

## Updating the Application

Railway automatically redeploys when you push to your GitHub repository:

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update application"
   git push origin main
   ```
3. Railway detects the push and triggers new deployment
4. Monitor deployment in Railway dashboard

## Rolling Back

To rollback to a previous version:

1. Go to service in Railway dashboard
2. Navigate to "Deployments" tab
3. Find the previous working deployment
4. Click "..." → "Redeploy"

## Database Backups

Railway PostgreSQL includes automatic backups:
- Backups are taken daily
- Retained for 7 days (Hobby plan)
- Retained for 14 days (Pro plan)

To manually backup:
```bash
railway connect postgres
pg_dump -Fc > backup.dump
```

## Support

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Project Issues: GitHub repository issues

## Additional Resources

- [Railway Multi-Service Deployments](https://docs.railway.app/deploy/deployments)
- [Railway Environment Variables](https://docs.railway.app/develop/variables)
- [Railway PostgreSQL](https://docs.railway.app/databases/postgresql)
