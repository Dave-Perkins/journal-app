# Email Notifications Setup Guide

## Overview
The app now sends email notifications to Michelle whenever a rider alerts her about a new entry. This guide will help you set up Gmail for development testing.

## Gmail Setup (Development)

### Step 1: Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Look for "2-Step Verification" and click "Enable"
3. Follow the prompts to complete 2FA setup

### Step 2: Generate an App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (custom name)" → type "Equestrian Journal"
3. Google will generate a 16-character password with spaces
4. Copy this password (remove spaces if any)

### Step 3: Configure .env File
1. Open `.env` file in the project root
2. Paste your App Password in the `EMAIL_HOST_PASSWORD` field:
   ```
   EMAIL_HOST_PASSWORD=your16characterpasswordhere
   ```
3. Keep `EMAIL_HOST_USER=ananab.tilps@gmail.com`
4. Keep `MICHELLE_EMAIL=ananab.tilps@gmail.com` (for testing)
5. Save the file

### Step 4: Restart the Development Server
```bash
source venv/bin/activate && python manage.py runserver
```

## How It Works

1. **Rider creates an entry** and clicks "Alert Michelle"
2. **Email sent** to Michelle with:
   - Rider's name and horse name
   - Entry submission timestamp
   - Preview of the entry text (first 300 characters)
   - Link to the dashboard
3. **Michelle receives email** and can log in to review and comment

## Testing Email

To test without setting up Gmail:

1. Check `settings.py` - if `EMAIL_HOST_PASSWORD` is empty, emails will fail gracefully
2. The entry will still be saved and marked as alerted
3. You'll see a warning message instead of success

## Production Configuration

When deploying to DigitalOcean, update `.env` with:

```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password
MICHELLE_EMAIL=michellelabarre@yahoo.com
```

Or better yet, use a service like:
- **SendGrid** (recommended for production)
- **AWS SES**
- DigitalOcean's mail server

## Troubleshooting

**"Email notification failed" message?**
- Check that `EMAIL_HOST_PASSWORD` is filled in `.env`
- Verify the 16-character password (no extra spaces)
- Check your inbox/spam folder for test emails

**Gmail blocking the connection?**
- Make sure 2FA is enabled
- Make sure you used an "App Password" (not your regular password)
- Check https://myaccount.google.com/apppasswords for the generated password

**Logs to check:**
```bash
# In your terminal running the dev server, look for error messages about SMTP
# Or check manage.py shell:
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'This is a test', 'from@example.com', ['to@example.com'])
```

## Security Note

⚠️ **IMPORTANT**: Never commit `.env` to version control! The `.env` file contains sensitive credentials.

Files that should never be committed:
- `.env` (contains passwords and API keys)
- `*.pyc` (compiled Python files)
- `db.sqlite3` (development database)
- `media/` (user uploads)

These are already in `.gitignore` by Django defaults.
