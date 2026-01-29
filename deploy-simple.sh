#!/bin/bash

#############################################
# HMS Simple Deployment (NO DOCKER)
# Direct installation on Ubuntu EC2
#############################################

set -e

APP_DIR="/opt/hms"
DOMAIN="vakverse.com"

echo "============================================"
echo "  HMS Deployment - NO DOCKER"
echo "============================================"

# Step 1: System Update
echo ""
echo "📦 Step 1: Updating system..."
sudo apt-get update
sudo apt-get upgrade -y

# Step 2: Install Python 3.11
echo ""
echo "🐍 Step 2: Installing Python..."
sudo apt-get install -y python3 python3-pip python3-venv

# Step 3: Install Node.js 20
echo ""
echo "📗 Step 3: Installing Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Step 4: Install Redis
echo ""
echo "⚡ Step 4: Installing Redis..."
sudo apt-get install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Step 5: Install Nginx
echo ""
echo "🌐 Step 5: Installing Nginx..."
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Step 6: Clone/Update Repository
echo ""
echo "📂 Step 6: Setting up application..."
cd $APP_DIR
sudo git pull origin main || true
sudo chown -R ubuntu:ubuntu $APP_DIR

# Step 7: Setup Backend
echo ""
echo "🔧 Step 7: Setting up Django Backend..."
cd $APP_DIR/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create .env file for backend
cat > .env << 'ENVFILE'
DEBUG=False
DJANGO_SECRET_KEY=SFsGagzE2nDMdYT1kz2k8IQJUEm8BKUthszJbg6K7RqReJvPVZ
ALLOWED_HOSTS=vakverse.com,www.vakverse.com,3.7.104.228,localhost,127.0.0.1

DB_ENGINE=django.db.backends.postgresql
DB_NAME=hms_db
DB_USER=hms_admin
DB_PASSWORD=7H8qzIwBQN7FCLi6CgeaiPCW
DB_HOST=hms-db.crk028ec0jqi.ap-south-1.rds.amazonaws.com
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

AWS_STORAGE_BUCKET_NAME=vakverse-hms-medical-files
AWS_S3_REGION_NAME=ap-south-1

AES_ENCRYPTION_KEY=d2XgVe95KXbEBB5uASEFCEZeUoP0YTuG
ENVFILE

# Run migrations
python manage.py migrate
python manage.py collectstatic --noinput

# Create superuser
python manage.py shell << 'PYTHON'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@vakverse.com', 'Admin123!')
    print('Superuser created!')
PYTHON

deactivate

# Step 8: Setup Frontend
echo ""
echo "⚛️ Step 8: Setting up Next.js Frontend..."
cd $APP_DIR/frontend

# Create .env.local for frontend
cat > .env.local << 'ENVFILE'
NEXT_PUBLIC_API_URL=https://www.vakverse.com/api
NEXTAUTH_URL=https://www.vakverse.com
ENVFILE

# Install dependencies and build
npm install --legacy-peer-deps
npm run build

# Step 9: Create Systemd Services
echo ""
echo "⚙️ Step 9: Creating system services..."

# Backend service (Gunicorn)
sudo tee /etc/systemd/system/hms-backend.service << 'SERVICE'
[Unit]
Description=HMS Django Backend
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/hms/backend
Environment="PATH=/opt/hms/backend/venv/bin"
ExecStart=/opt/hms/backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 hms.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

# Frontend service (Next.js)
sudo tee /etc/systemd/system/hms-frontend.service << 'SERVICE'
[Unit]
Description=HMS Next.js Frontend
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/hms/frontend
Environment="NODE_ENV=production"
Environment="PORT=3000"
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

# Celery service
sudo tee /etc/systemd/system/hms-celery.service << 'SERVICE'
[Unit]
Description=HMS Celery Worker
After=network.target redis.service

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/hms/backend
Environment="PATH=/opt/hms/backend/venv/bin"
ExecStart=/opt/hms/backend/venv/bin/celery -A hms worker -l info
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

# Reload and start services
sudo systemctl daemon-reload
sudo systemctl enable hms-backend hms-frontend hms-celery
sudo systemctl restart hms-backend hms-frontend hms-celery

# Step 10: Configure Nginx
echo ""
echo "🌐 Step 10: Configuring Nginx..."

sudo tee /etc/nginx/sites-available/hms << 'NGINX'
server {
    listen 80;
    server_name vakverse.com www.vakverse.com 3.7.104.228;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 50M;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8000/admin/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /opt/hms/backend/staticfiles/;
    }
}
NGINX

sudo ln -sf /etc/nginx/sites-available/hms /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# Step 11: Check status
echo ""
echo "============================================"
echo "  🎉 DEPLOYMENT COMPLETE!"
echo "============================================"
echo ""
echo "Service Status:"
sudo systemctl status hms-backend --no-pager | head -5
sudo systemctl status hms-frontend --no-pager | head -5
echo ""
echo "URLs:"
echo "  Frontend: http://3.7.104.228"
echo "  Admin: http://3.7.104.228/admin"
echo "  API: http://3.7.104.228/api/"
echo ""
echo "Admin Login:"
echo "  Username: admin"
echo "  Password: Admin123!"
echo ""
echo "For SSL, run:"
echo "  sudo certbot --nginx -d vakverse.com -d www.vakverse.com"
