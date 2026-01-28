#!/bin/bash

#############################################
# HMS Deployment Script for EC2
# Run this on your EC2 server
#############################################

set -e

echo "============================================"
echo "  HMS Deployment Script"
echo "  Domain: www.vakverse.com"
echo "============================================"

# Variables
APP_DIR="/opt/hms"
DOMAIN="vakverse.com"
EMAIL="admin@vakverse.com"

# Step 1: Update system
echo ""
echo "📦 Step 1: Updating system..."
sudo apt-get update
sudo apt-get upgrade -y

# Step 2: Install dependencies
echo ""
echo "📦 Step 2: Installing dependencies..."
sudo apt-get install -y docker.io docker-compose-v2 nginx certbot python3-certbot-nginx git

# Step 3: Start Docker
echo ""
echo "🐳 Step 3: Starting Docker..."
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Step 4: Clone repository
echo ""
echo "📂 Step 4: Setting up application..."
if [ -d "$APP_DIR" ]; then
    cd $APP_DIR
    sudo git pull origin main
else
    sudo git clone https://github.com/Om-mac/HMS.git $APP_DIR
    sudo chown -R $USER:$USER $APP_DIR
fi

cd $APP_DIR

# Step 5: Copy environment file
echo ""
echo "⚙️ Step 5: Setting up environment..."
if [ -f ".env.production" ]; then
    cp .env.production .env
    echo "   ✅ Environment file configured"
else
    echo "   ⚠️ Please copy .env.production to .env and update credentials"
fi

# Step 6: Configure Nginx
echo ""
echo "🌐 Step 6: Configuring Nginx..."

sudo tee /etc/nginx/sites-available/hms << 'NGINX'
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name vakverse.com www.vakverse.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name vakverse.com www.vakverse.com;

    # SSL certificates (will be added by certbot)
    ssl_certificate /etc/letsencrypt/live/vakverse.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vakverse.com/privkey.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 50M;
    }
    
    # Django Admin
    location /admin/ {
        proxy_pass http://localhost:8000/admin/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        proxy_pass http://localhost:8000/static/;
    }
}
NGINX

# Enable site (without SSL first for initial setup)
sudo tee /etc/nginx/sites-available/hms-initial << 'NGINX'
server {
    listen 80;
    server_name vakverse.com www.vakverse.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /admin/ {
        proxy_pass http://localhost:8000/admin/;
        proxy_set_header Host $host;
    }
}
NGINX

sudo ln -sf /etc/nginx/sites-available/hms-initial /etc/nginx/sites-enabled/hms
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

echo "   ✅ Nginx configured"

# Step 7: Build and start Docker containers
echo ""
echo "🐳 Step 7: Building Docker containers..."
cd $APP_DIR

# Create docker-compose override for production
cat > docker-compose.override.yml << 'OVERRIDE'
version: '3.8'

services:
  backend:
    environment:
      - DEBUG=False
    restart: always
    
  frontend:
    environment:
      - NODE_ENV=production
    restart: always
    
  celery:
    restart: always
    
  redis:
    restart: always
OVERRIDE

# Start containers
sudo docker compose -f docker-compose.yml -f docker-compose.override.yml up -d --build

echo "   ✅ Docker containers started"

# Step 8: Run database migrations
echo ""
echo "🗄️ Step 8: Running database migrations..."
sleep 10  # Wait for containers to be ready
sudo docker compose exec -T backend python manage.py migrate
sudo docker compose exec -T backend python manage.py collectstatic --noinput

echo "   ✅ Migrations complete"

# Step 9: Create superuser
echo ""
echo "👤 Step 9: Creating superuser..."
sudo docker compose exec -T backend python manage.py shell << 'PYTHON'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@vakverse.com', 'ChangeThisPassword123!')
    print('Superuser created!')
else:
    print('Superuser already exists')
PYTHON

echo ""
echo "============================================"
echo "  🎉 DEPLOYMENT COMPLETE!"
echo "============================================"
echo ""
echo "📝 Final Steps:"
echo ""
echo "1. Get SSL Certificate (run this after DNS propagates):"
echo "   sudo certbot --nginx -d vakverse.com -d www.vakverse.com -m $EMAIL --agree-tos"
echo ""
echo "2. After SSL is installed, switch to full Nginx config:"
echo "   sudo ln -sf /etc/nginx/sites-available/hms /etc/nginx/sites-enabled/hms"
echo "   sudo nginx -t && sudo systemctl reload nginx"
echo ""
echo "3. Access your application:"
echo "   - Frontend: https://www.vakverse.com"
echo "   - Admin: https://www.vakverse.com/admin"
echo "   - API: https://www.vakverse.com/api/"
echo ""
echo "4. Default Admin Login:"
echo "   Username: admin"
echo "   Password: ChangeThisPassword123!"
echo "   ⚠️ CHANGE THIS PASSWORD IMMEDIATELY!"
echo ""
echo "============================================"
