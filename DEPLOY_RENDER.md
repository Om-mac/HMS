# HMS Deployment Guide - Render

## Quick Deploy to Render

### Option 1: Blueprint (Recommended)
1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **New** → **Blueprint**
4. Connect your GitHub repository
5. Render will automatically detect `render.yaml` and create all services

### Option 2: Manual Setup

#### 1. Create PostgreSQL Database
- Go to Render Dashboard → **New** → **PostgreSQL**
- Name: `hms-db`
- Region: Singapore (closest to India)
- Plan: Starter ($7/month) or Free (for testing)
- Note the **Internal Database URL**

#### 2. Create Redis Instance
- Go to Render Dashboard → **New** → **Redis**
- Name: `hms-redis`
- Region: Singapore
- Plan: Starter
- Note the **Internal Redis URL**

#### 3. Deploy Backend (Django)
- Go to Render Dashboard → **New** → **Web Service**
- Connect your GitHub repo
- Settings:
  - **Name**: `hms-backend`
  - **Root Directory**: `backend`
  - **Runtime**: Python 3
  - **Build Command**: `./build.sh`
  - **Start Command**: `gunicorn hms.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
  
- Environment Variables:
  ```
  DEBUG=False
  SECRET_KEY=<generate-a-secure-key>
  DATABASE_URL=<from-step-1>
  REDIS_URL=<from-step-2>
  ALLOWED_HOSTS=.onrender.com,vakverse.com,www.vakverse.com
  CORS_ALLOWED_ORIGINS=https://hms-frontend.onrender.com,https://vakverse.com
  AES_ENCRYPTION_KEY=<generate-32-char-key>
  AWS_ACCESS_KEY_ID=<your-aws-key>
  AWS_SECRET_ACCESS_KEY=<your-aws-secret>
  AWS_STORAGE_BUCKET_NAME=<your-s3-bucket>
  ```

#### 4. Deploy Frontend (Next.js)
- Go to Render Dashboard → **New** → **Web Service**
- Connect your GitHub repo
- Settings:
  - **Name**: `hms-frontend`
  - **Root Directory**: `frontend`
  - **Runtime**: Node
  - **Build Command**: `npm install && npm run build`
  - **Start Command**: `npm start`
  
- Environment Variables:
  ```
  NEXT_PUBLIC_API_URL=https://hms-backend.onrender.com
  ```

#### 5. Deploy Celery Worker (Optional - for background tasks)
- Go to Render Dashboard → **New** → **Background Worker**
- Connect your GitHub repo
- Settings:
  - **Name**: `hms-celery`
  - **Root Directory**: `backend`
  - **Runtime**: Python 3
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `celery -A hms worker --loglevel=info`
- Add same env vars as backend

## Custom Domain Setup

1. In Render Dashboard, go to your frontend service
2. Click **Settings** → **Custom Domains**
3. Add `vakverse.com` and `www.vakverse.com`
4. Update DNS at your domain registrar:
   - Add CNAME record: `www` → `hms-frontend.onrender.com`
   - Add A record for root domain (Render will provide IP)

## Viewing Logs

```bash
# In Render Dashboard, click on any service → "Logs" tab
# Or use Render CLI:
render logs --service hms-backend --tail
```

## Costs (Starter Plan)

| Service | Cost/Month |
|---------|-----------|
| Backend Web Service | $7 |
| Frontend Web Service | $7 |
| PostgreSQL | $7 |
| Redis | $7 |
| Celery Worker | $7 |
| **Total** | **~$35/month** |

*Free tier available for testing (with limitations)*

## Automatic Deployments

Render automatically deploys when you push to your connected branch (usually `main`).

## Troubleshooting

### Check Logs
- Go to service → **Logs** tab

### Database Migrations
Migrations run automatically via `build.sh`. To run manually:
- Go to service → **Shell** tab
- Run: `cd backend && python manage.py migrate`

### Restart Service
- Go to service → Click **Manual Deploy** → **Clear build cache & deploy**
