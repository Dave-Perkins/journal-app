# Deployment Files

This folder contains all configuration files needed for production deployment to DigitalOcean.

## Files

### `deploy.sh`
Automated deployment script that sets up everything on a fresh Ubuntu 22.04 LTS droplet.

**Usage:**
```bash
ssh root@143.198.2.6
git clone https://github.com/yourusername/journal-app.git /var/www/journal-app
cd /var/www/journal-app
chmod +x deploy/deploy.sh
sudo deploy/deploy.sh
```

### `settings_production.py`
Django production settings using PostgreSQL, Gunicorn, and environment variables.

Features:
- PostgreSQL database backend
- Security hardening (HTTPS, HSTS, secure cookies)
- Email configuration
- Static file handling with ManifestStaticFilesStorage
- Error logging

**Copied to:** `/var/www/journal-app/journalapp/settings_production.py`

### `nginx.conf`
Nginx reverse proxy configuration.

Features:
- Proxies requests to Gunicorn
- Serves static files directly
- Handles media uploads
- Configured for HTTP (SSL commented out)

**Copied to:** `/etc/nginx/sites-available/journal-app`

### `gunicorn_systemd.service`
Systemd service file for Gunicorn application server.

Features:
- Runs as `journalapp` user
- 3 worker processes
- Automatic restart on failure
- Loads `.env.production` for environment variables
- Logs to `/var/log/journal-app/`

**Copied to:** `/etc/systemd/system/journal-app.service`

## Deployment Process

1. SSH to droplet
2. Clone repo
3. Run `deploy.sh` script
4. Edit `.env.production` with production values
5. Restart services
6. Visit http://143.198.2.6

## Post-Deployment Configuration

Edit `.env.production`:
```bash
sudo nano /var/www/journal-app/.env.production
```

Update:
- `SECRET_KEY` - Use a random secure key
- `DATABASE_PASSWORD` - Change from default
- `EMAIL_HOST_PASSWORD` - Gmail app password
- `MICHELLE_EMAIL` - Use production email

## Service Management

```bash
# Start/stop application
sudo systemctl restart journal-app
sudo systemctl status journal-app

# View logs
sudo journalctl -u journal-app -f

# Start/stop web server
sudo systemctl restart nginx

# Enable on boot
sudo systemctl enable journal-app
sudo systemctl enable nginx
```

## Troubleshooting

See `../DEPLOYMENT_GUIDE.md` for detailed troubleshooting and manual deployment steps.

---

**Deployment Target:** DigitalOcean Ubuntu 22.04 LTS  
**IP Address:** 143.198.2.6  
**Created:** January 10, 2026
