#!/bin/bash
# Equestrian Journal App - DigitalOcean Deployment Script
# Ubuntu 22.04 LTS
# Run this script on the droplet as root

set -e  # Exit on any error

echo "=========================================="
echo "Equestrian Journal - Production Deployment"
echo "=========================================="

# Update system
echo "[1/10] Updating system packages..."
apt-get update
apt-get upgrade -y

# Install system dependencies
echo "[2/10] Installing system dependencies..."
apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    postgresql \
    postgresql-contrib \
    nginx \
    supervisor \
    git \
    curl \
    wget \
    build-essential \
    libpq-dev

# Create application user
echo "[3/10] Creating application user..."
if ! id -u journalapp > /dev/null 2>&1; then
    useradd -m -s /bin/bash journalapp
    echo "Created journalapp user"
else
    echo "journalapp user already exists"
fi

# Create application directory
echo "[4/10] Setting up application directory..."
mkdir -p /var/www/journal-app
cd /var/www/journal-app
chown -R journalapp:journalapp /var/www/journal-app

# Clone or pull repository (adjust git URL as needed)
echo "[5/10] Cloning application code..."
sudo -u journalapp git clone https://github.com/yourusername/journal-app.git . 2>/dev/null || sudo -u journalapp git -C /var/www/journal-app reset --hard origin/master

# Create virtual environment
echo "[6/10] Setting up Python virtual environment..."
sudo -u journalapp python3 -m venv venv
sudo -u journalapp venv/bin/pip install --upgrade pip
sudo -u journalapp venv/bin/pip install -r requirements.txt
sudo -u journalapp venv/bin/pip install gunicorn

# Set up PostgreSQL database
echo "[7/10] Setting up PostgreSQL database..."
sudo -u postgres psql <<EOF
CREATE DATABASE journal_db;
CREATE USER journal_user WITH PASSWORD 'secure_password_here';
ALTER ROLE journal_user SET client_encoding TO 'utf8';
ALTER ROLE journal_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE journal_user SET default_transaction_deferrable TO on;
ALTER ROLE journal_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE journal_db TO journal_user;
EOF

# Copy production settings
echo "[8/10] Copying configuration files..."
cp /var/www/journal-app/deploy/settings_production.py /var/www/journal-app/journalapp/settings_production.py
cp /var/www/journal-app/deploy/gunicorn_systemd.service /etc/systemd/system/journal-app.service
cp /var/www/journal-app/deploy/nginx.conf /etc/nginx/sites-available/journal-app
ln -sf /etc/nginx/sites-available/journal-app /etc/nginx/sites-enabled/journal-app
rm -f /etc/nginx/sites-enabled/default

# Create .env file for production (user must fill in sensitive values)
echo "[9/10] Creating .env file for production..."
cat > /var/www/journal-app/.env.production << 'ENVFILE'
# Production Environment Variables
DEBUG=False
SECRET_KEY=change-this-to-a-random-secure-key
ALLOWED_HOSTS=143.198.2.6

# Database
DATABASE_URL=postgresql://journal_user:secure_password_here@localhost:5432/journal_db

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password
MICHELLE_EMAIL=michellelabarre@yahoo.com
ENVFILE

chown journalapp:journalapp /var/www/journal-app/.env.production
chmod 600 /var/www/journal-app/.env.production

# Run migrations
echo "[10/10] Running database migrations..."
cd /var/www/journal-app
sudo -u journalapp venv/bin/python manage.py collectstatic --noinput --settings=journalapp.settings_production
sudo -u journalapp venv/bin/python manage.py migrate --settings=journalapp.settings_production

# Enable and start services
systemctl daemon-reload
systemctl enable journal-app.service
systemctl restart journal-app.service
systemctl enable nginx
systemctl restart nginx

echo ""
echo "=========================================="
echo "✓ Deployment Complete!"
echo "=========================================="
echo ""
echo "IMPORTANT: Edit these files before the app is fully live:"
echo "1. /var/www/journal-app/.env.production"
echo "   - Set a secure SECRET_KEY"
echo "   - Update EMAIL credentials"
echo "   - Update database password"
echo ""
echo "2. /etc/nginx/sites-available/journal-app"
echo "   - Update server_name if using a domain"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u journal-app -f"
echo ""
echo "To restart the app:"
echo "  sudo systemctl restart journal-app"
echo ""
echo "App should be live at: http://143.198.2.6"
echo ""
