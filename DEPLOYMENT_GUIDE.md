# DigitalOcean Deployment Guide

**Equestrian Journal App**  
**Target:** Ubuntu 22.04 LTS at 143.198.2.6  
**Updated:** January 10, 2026

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Deployment](#quick-deployment)
3. [Manual Deployment](#manual-deployment)
4. [Post-Deployment Configuration](#post-deployment-configuration)
5. [SSL/HTTPS Setup](#ssl-https-setup)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

---

## Prerequisites

### Local Setup (Your Machine)
- Django app ready to deploy (this journal app)
- Git repository created and pushed (if using automated deployment)
- SSH access to droplet (password or key-based)

### Droplet Setup (Already Done)
- ✅ Ubuntu 22.04 LTS
- ✅ IP: 143.198.2.6
- ✅ Root SSH access

---

## Quick Deployment

### Option 1: Automated Deployment Script (Recommended)

1. **SSH into your droplet:**
   ```bash
   ssh root@143.198.2.6
   ```

2. **Clone the app repository:**
   ```bash
   git clone https://github.com/yourusername/journal-app.git /var/www/journal-app
   cd /var/www/journal-app
   ```

3. **Run the deployment script:**
   ```bash
   chmod +x deploy/deploy.sh
   sudo deploy/deploy.sh
   ```

4. **Configure production environment:**
   ```bash
   nano /var/www/journal-app/.env.production
   ```
   Update:
   - `SECRET_KEY` - Run this in Python to generate: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
   - `EMAIL_HOST_PASSWORD` - Your Gmail app password
   - `DATABASE_PASSWORD` - Change from default

5. **Restart the application:**
   ```bash
   sudo systemctl restart journal-app
   sudo systemctl restart nginx
   ```

6. **Visit:** http://143.198.2.6

---

## Manual Deployment

If you prefer to set up step-by-step:

### Step 1: System Setup

```bash
ssh root@143.198.2.6

# Update system
apt-get update && apt-get upgrade -y

# Install dependencies
apt-get install -y python3-pip python3-venv python3-dev postgresql \
    postgresql-contrib nginx git build-essential libpq-dev
```

### Step 2: Create App User & Directory

```bash
useradd -m -s /bin/bash journalapp
mkdir -p /var/www/journal-app
chown -R journalapp:journalapp /var/www/journal-app
cd /var/www/journal-app
```

### Step 3: Clone Repository

```bash
sudo -u journalapp git clone https://github.com/yourusername/journal-app.git .
```

### Step 4: Set Up Python Environment

```bash
sudo -u journalapp python3 -m venv venv
sudo -u journalapp venv/bin/pip install --upgrade pip
sudo -u journalapp venv/bin/pip install -r requirements.txt
sudo -u journalapp venv/bin/pip install gunicorn
```

### Step 5: PostgreSQL Setup

```bash
sudo -u postgres psql << 'EOF'
CREATE DATABASE journal_db;
CREATE USER journal_user WITH PASSWORD 'your_secure_password';
ALTER ROLE journal_user SET client_encoding TO 'utf8';
ALTER ROLE journal_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE journal_user SET default_transaction_deferrable TO on;
GRANT ALL PRIVILEGES ON DATABASE journal_db TO journal_user;
EOF
```

### Step 6: Configure Django

```bash
# Create production .env file
cat > /var/www/journal-app/.env.production << 'EOF'
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=143.198.2.6
DATABASE_PASSWORD=your_secure_password
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
MICHELLE_EMAIL=michellelabarre@yahoo.com
EOF

# Set permissions
chown journalapp:journalapp /var/www/journal-app/.env.production
chmod 600 /var/www/journal-app/.env.production

# Run migrations
cd /var/www/journal-app
sudo -u journalapp venv/bin/python manage.py migrate --settings=journalapp.settings_production
sudo -u journalapp venv/bin/python manage.py collectstatic --noinput --settings=journalapp.settings_production
```

### Step 7: Gunicorn Setup

```bash
# Copy systemd service file
cp /var/www/journal-app/deploy/gunicorn_systemd.service /etc/systemd/system/journal-app.service

# Enable and start
systemctl daemon-reload
systemctl enable journal-app.service
systemctl start journal-app.service

# Check status
systemctl status journal-app.service
```

### Step 8: Nginx Setup

```bash
# Copy and enable site
cp /var/www/journal-app/deploy/nginx.conf /etc/nginx/sites-available/journal-app
ln -sf /etc/nginx/sites-available/journal-app /etc/nginx/sites-enabled/journal-app
rm -f /etc/nginx/sites-enabled/default

# Test and enable
nginx -t
systemctl enable nginx
systemctl restart nginx
```

---

## Post-Deployment Configuration

### 1. Create Superuser for Admin

```bash
cd /var/www/journal-app
sudo -u journalapp venv/bin/python manage.py createsuperuser --settings=journalapp.settings_production
```

### 2. Create Sample Data (Optional)

```bash
sudo -u journalapp venv/bin/python manage.py create_sample_data --settings=journalapp.settings_production
```

### 3. Set Up Log Directory

```bash
mkdir -p /var/log/journal-app
chown journalapp:journalapp /var/log/journal-app
chmod 755 /var/log/journal-app
```

### 4. Test the App

```bash
# Check Gunicorn
sudo systemctl status journal-app

# Check Nginx
sudo systemctl status nginx

# View logs
sudo journalctl -u journal-app -f
```

Visit: http://143.198.2.6

---

## SSL/HTTPS Setup

### Using Let's Encrypt with Certbot

```bash
# Install Certbot
apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
certbot certonly --standalone -d 143.198.2.6

# Or if using a domain instead of IP
certbot certonly --standalone -d your-domain.com

# Update Nginx configuration (uncomment SSL sections in nginx.conf)
nano /etc/nginx/sites-available/journal-app

# Test and reload
nginx -t
systemctl reload nginx
```

**Note:** Let's Encrypt doesn't support bare IPs. If using only the IP, you'll need a self-signed certificate or switch to a domain.

For a domain setup:
1. Point your domain to 143.198.2.6 in DNS
2. Run certbot with the domain
3. Update nginx config with domain name and cert paths

---

## Troubleshooting

### App Not Loading

```bash
# Check Gunicorn status
sudo systemctl status journal-app

# View Gunicorn logs
sudo tail -50 /var/log/journal-app/gunicorn-error.log

# Check Django logs
sudo journalctl -u journal-app -f

# Restart if needed
sudo systemctl restart journal-app
```

### Nginx Issues

```bash
# Check syntax
sudo nginx -t

# View error log
sudo tail -50 /var/log/nginx/error.log

# Restart
sudo systemctl restart nginx
```

### Database Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Connect to database
sudo -u postgres psql -d journal_db

# Check app database connection
cd /var/www/journal-app
sudo -u journalapp venv/bin/python manage.py dbshell --settings=journalapp.settings_production
```

### Email Not Sending

```bash
# Test email configuration
cd /var/www/journal-app
sudo -u journalapp venv/bin/python manage.py shell --settings=journalapp.settings_production
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'This is a test', 'from@example.com', ['to@example.com'])
```

---

## Maintenance

### Updating the App

```bash
cd /var/www/journal-app

# Pull latest code
sudo -u journalapp git pull origin main

# Collect static files
sudo -u journalapp venv/bin/python manage.py collectstatic --noinput --settings=journalapp.settings_production

# Run migrations if any
sudo -u journalapp venv/bin/python manage.py migrate --settings=journalapp.settings_production

# Restart app
sudo systemctl restart journal-app
```

### Backup Database

```bash
# Backup PostgreSQL
sudo -u postgres pg_dump journal_db > /backups/journal_db_$(date +%Y%m%d_%H%M%S).sql

# Backup media files
tar -czf /backups/media_$(date +%Y%m%d_%H%M%S).tar.gz /var/www/journal-app/media/
```

### View Live Logs

```bash
# Application logs
sudo journalctl -u journal-app -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# All system logs
sudo tail -f /var/log/syslog
```

### Monitor Disk Usage

```bash
df -h
du -sh /var/www/journal-app
du -sh /var/www/journal-app/media
```

---

## Quick Reference Commands

```bash
# SSH to droplet
ssh root@143.198.2.6

# Restart application
sudo systemctl restart journal-app

# Restart web server
sudo systemctl restart nginx

# View application status
sudo systemctl status journal-app

# View live logs
sudo journalctl -u journal-app -f

# Update code
cd /var/www/journal-app && sudo -u journalapp git pull origin main

# Manage Django
sudo -u journalapp /var/www/journal-app/venv/bin/python /var/www/journal-app/manage.py [command] --settings=journalapp.settings_production
```

---

## Support

For issues or questions:
1. Check logs: `sudo journalctl -u journal-app -f`
2. Review nginx error logs: `sudo tail /var/log/nginx/error.log`
3. Test database connection: `sudo -u postgres psql -d journal_db`

---

**Deployment completed on:** January 10, 2026
