# 🚀 Implementation Guide: AI Quiz + Summarization System

Complete walkthrough for deploying and using the production-ready system.

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Local Development Setup](#local-development-setup)
3. [Database Configuration](#database-configuration)
4. [Backend Configuration](#backend-configuration)
5. [Frontend Configuration](#frontend-configuration)
6. [Running the System](#running-the-system)
7. [Testing the APIs](#testing-the-apis)
8. [Production Deployment](#production-deployment)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### Required Software
- [ ] Python 3.9 or higher
- [ ] Node.js 16 or higher
- [ ] PostgreSQL 12 or higher
- [ ] Git

### Hardware Requirements
- [ ] Minimum 2GB RAM for development
- [ ] 4GB+ RAM for production
- [ ] 10GB+ storage for data and models

### Accounts & Services
- [ ] PostgreSQL database created
- [ ] JWT secret key generated (minimum 32 characters)
- [ ] CORS origins configured

---

## Local Development Setup

### Step 1: Clone & Navigate
```bash
cd summarization_project
cd summarization
```

### Step 2: Run Automated Setup

**On Windows:**
```bash
setup.bat
```

**On Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

Or manual setup:

```bash
# Backend
cd ai_core
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

---

## Database Configuration

### Creating PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE summarization_db;
CREATE USER summarization_user WITH PASSWORD 'your_secure_password';
ALTER ROLE summarization_user SET client_encoding TO 'utf8';
ALTER ROLE summarization_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE summarization_user SET default_transaction_deferrable TO on;
ALTER ROLE summarization_user SET default_transaction_read_committed TO off;
GRANT ALL PRIVILEGES ON DATABASE summarization_db TO summarization_user;

# Exit
\q
```

### Verify Connection
```bash
psql -U summarization_user -d summarization_db -h localhost
```

---

## Backend Configuration

### Step 1: Environment Variables

Create `ai_core/.env`:

```env
# === Application ===
DEBUG=False
APP_NAME="AI Quiz & Summarization System"
APP_VERSION="1.0.0"

# === Database ===
DATABASE_URL=postgresql://summarization_user:your_secure_password@localhost:5432/summarization_db

# === JWT Security ===
JWT_SECRET_KEY=your-super-secret-key-min-32-characters-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
JWT_REFRESH_EXPIRATION_DAYS=30

# === Summarization ===
SUMMARY_MAX_SENTENCES=5
DEFAULT_LANGUAGE=vi

# === CORS ===
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://yourdomain.com
```

### Step 2: Generate Secure JWT Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3: Initialize Database

```bash
cd ai_core
python -c "from database import init_db; init_db()"
```

### Step 4: Test Backend

```bash
python main.py
```

Visit: `http://localhost:8000/api/docs`

---

## Frontend Configuration

### Step 1: Environment Variables

Create `frontend/.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Step 2: Build Configuration

The Vite config is already set up in `vite.config.js`

### Step 3: Test Frontend

```bash
cd frontend
npm run dev
```

Visit: `http://localhost:5173`

---

## Running the System

### Development Mode (3 Terminals)

**Terminal 1 - Backend:**
```bash
cd ai_core
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
# Runs on: http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Runs on: http://localhost:5173
```

**Terminal 3 (Optional) - Database Monitor:**
```bash
# Monitor PostgreSQL if needed
psql -U summarization_user -d summarization_db -h localhost
```

### Quick Access
- 🌐 Frontend: http://localhost:5173
- 🔌 Backend API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/api/docs
- 🧪 API Testing: http://localhost:8000/api/redoc

---

## Testing the APIs

### 1. Register a New User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

### 3. Get User Profile (Protected)

```bash
curl -X GET "http://localhost:8000/user/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Submit Quiz

```bash
curl -X POST "http://localhost:8000/quiz/submit" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "article_title": "Sample Article",
    "article_text": "This is the article content...",
    "summary_text": "This is the summary...",
    "questions": [
      {
        "id": 1,
        "question": "What is the main topic?",
        "options": ["A", "B", "C", "D"],
        "correct_answer": 0,
        "user_answer": 0,
        "is_correct": true
      }
    ],
    "time_taken_seconds": 300,
    "difficulty": "medium",
    "category": "Technology",
    "language": "en"
  }'
```

### 5. Get Dashboard

```bash
curl -X GET "http://localhost:8000/analytics/dashboard" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. Get Leaderboard

```bash
curl -X GET "http://localhost:8000/leaderboard/?limit=50" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Production Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv postgresql postgresql-contrib
sudo apt install -y nodejs npm

# Install Nginx
sudo apt install -y nginx

# Install Gunicorn
pip install gunicorn
```

### 2. Backend Deployment

Create `/etc/systemd/system/summarization-api.service`:

```ini
[Unit]
Description=AI Summarization API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/summarization/ai_core
Environment="PATH=/var/www/summarization/ai_core/venv/bin"
ExecStart=/var/www/summarization/ai_core/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 main:app

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable summarization-api
sudo systemctl start summarization-api
```

### 3. Frontend Deployment

Build frontend:
```bash
cd frontend
npm run build
# Creates dist/ folder
```

### 4. Nginx Configuration

Create `/etc/nginx/sites-available/summarization`:

```nginx
upstream summarization_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /var/www/summarization/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://summarization_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://summarization_api/health;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/summarization /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. SSL/TLS with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 6. Database Backups

Create backup script `backup.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/database"
mkdir -p $BACKUP_DIR

pg_dump -U summarization_user summarization_db | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

Add to crontab:
```bash
sudo crontab -e
# 2 AM daily backup
0 2 * * * /root/backup.sh
```

---

## Monitoring & Maintenance

### View Logs

Backend:
```bash
sudo journalctl -u summarization-api -f
```

Nginx:
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Maintenance

```bash
# Connect to database
psql -U summarization_user -d summarization_db

# Vacuum and analyze
VACUUM ANALYZE;

# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE schemaname NOT IN ('pg_catalog', 'information_schema') 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Performance Monitoring

```bash
# CPU and memory usage
top -u www-data

# Disk space
df -h

# Database connections
psql -U summarization_user -d summarization_db -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Problem:** Database connection refused
```bash
# Solution: Check PostgreSQL is running
sudo systemctl status postgresql
# Or start it
sudo systemctl start postgresql
```

**Problem:** Port 8000 already in use
```bash
# Solution: Kill process or use different port
lsof -i :8000
kill -9 <PID>
# Or change port in main.py
```

### Frontend Issues

**Problem:** API calls fail with CORS error
```bash
# Solution: Check CORS_ORIGINS in .env
# Must include frontend URL
CORS_ORIGINS=http://localhost:5173
```

**Problem:** Build fails with node_modules errors
```bash
# Solution: Clean install
rm -rf node_modules package-lock.json
npm install
```

### Database Issues

**Problem:** "FATAL: remaining connection slots are reserved"
```bash
# Solution: Close connections and increase max_connections
psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='summarization_db';"
```

### Production Issues

**Problem:** Gunicorn workers keep dying
```bash
# Solution: Increase memory and worker count in service file
ExecStart=/var/www/summarization/ai_core/venv/bin/gunicorn -w 2 -b 127.0.0.1:8000 --timeout 120 main:app
```

---

## Security Hardening

### Change Default Credentials
```bash
# PostgreSQL user password
ALTER USER summarization_user WITH PASSWORD 'new_strong_password';
```

### Update JWT Secret
```bash
# Generate new secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Update in .env
```

### Enable HTTPS
```bash
# Get SSL certificate with Let's Encrypt
sudo certbot certonly --standalone -d your-domain.com
```

### Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## Next Steps

1. ✅ Set up local development environment
2. ✅ Test all API endpoints
3. ✅ Create test user accounts
4. ✅ Test quiz workflow end-to-end
5. ✅ Deploy to production
6. ✅ Set up monitoring
7. ✅ Create backup strategy
8. ✅ Document custom modifications

---

## Support Resources

- 📖 Full Documentation: See SYSTEM_DOCS.md
- 🐛 Report Issues: GitHub Issues
- 💬 Community: Discord Server
- 📧 Email Support: support@example.com

---

**Last Updated:** January 2024  
**Version:** 1.0.0
