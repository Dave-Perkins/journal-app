# Equestrian Journal App - Setup Guide

## Project Overview
A Django-based web application for equestrian riders to log journal entries with reflection notes and photos. Head trainer Michelle can review entries and provide feedback.

## Features Implemented

### Core Functionality
- ✅ **Login System**: Riders select their horse and name to log in
- ✅ **Journal Entries**: Create entries with text content and image uploads
- ✅ **Entry Management**: View, browse, and manage journal history
- ✅ **Alerts**: Notify Michelle when a new entry needs review
- ✅ **Comments**: Michelle can add comments to entries (admin interface)

### Database Models
- **Horse**: Represents individual horses (unique names)
- **Rider**: Links riders to horses (multiple riders per horse possible)
- **JournalEntry**: User-generated content with text and images, tracks if Michelle was alerted
- **Comment**: Michelle's feedback on entries

## Installation & Setup

### 1. Clone/Navigate to Project
```bash
cd /Users/dperkins/Desktop/journal-app
```

### 2. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 3. Database Setup (Already Done)
Migrations have been created and applied. Sample data is loaded. If you need to reset:
```bash
python manage.py migrate
python manage.py create_sample_data
```

### 4. Create Admin User
```bash
python manage.py createsuperuser
# Follow prompts to create username/password
```

### 5. Run Development Server
```bash
python manage.py runserver
```

Server will run at `http://localhost:8000`

## Using the Application

### Test Data
Sample horses and riders have been created:
- **Spirit**: Sarah, Emma, John
- **Thunder**: Mike, Lisa
- **Luna**: Alex, Jordan, Casey
- **Midnight**: Sam, Taylor

Select any horse and rider to log in.

### Admin Interface
Access at `http://localhost:8000/admin/`
- View and manage horses, riders, journal entries
- Add/edit comments for entries (as Michelle)
- Track which entries have alerts sent

## Project Structure
```
journal-app/
├── journalapp/              # Django project settings
│   ├── settings.py         # Configuration
│   ├── urls.py             # Main URL routing
│   └── wsgi.py
├── journal/                 # Main Django app
│   ├── models.py           # Database models (Horse, Rider, JournalEntry, Comment)
│   ├── views.py            # View logic for all pages
│   ├── urls.py             # App URL routing
│   ├── forms.py            # Django forms
│   ├── admin.py            # Admin interface setup
│   ├── templates/journal/  # HTML templates
│   │   ├── base.html           # Base template with styling
│   │   ├── login.html          # Login page
│   │   ├── dashboard.html      # Main dashboard
│   │   ├── create_entry.html   # New entry form
│   │   └── entry_detail.html   # Full entry + comments view
│   └── management/commands/
│       └── create_sample_data.py  # Management command for test data
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── PROJECT.md             # Project specifications
```

## Features Not Yet Implemented

### Michelle's Admin Interface
Currently, Michelle must use Django admin to view alerts and add comments. Next step would be to create:
- A dedicated interface for Michelle to see recent alerts
- Email notifications when a rider alerts her
- Quick-comment interface without admin backend

### Additional Features to Consider
- Edit/delete entries (currently read-only after creation)
- Search/filter entries by date or keywords
- Share entries with other riders
- Print-friendly entry view
- Export entries as PDF

## Deployment to DigitalOcean

When ready to deploy:
1. Install Gunicorn: `pip install gunicorn`
2. Install Nginx on your Droplet
3. Configure PostgreSQL database (replace SQLite)
4. Update `settings.py` with production settings (DEBUG=False, ALLOWED_HOSTS, SECRET_KEY)
5. Collect static files: `python manage.py collectstatic`
6. Create systemd service for Gunicorn
7. Configure Nginx as reverse proxy
8. Set up SSL with Let's Encrypt

See `DEPLOYMENT_NOTES.md` (to be created) for detailed steps.

## Development Notes

### Key Views
- `login_view`: Custom session-based login (no user accounts needed)
- `dashboard_view`: List all entries for logged-in rider
- `create_entry_view`: Form to create new entries
- `entry_detail_view`: Full entry display with Michelle's comments
- `alert_michelle_view`: Mark entry as needing review
- `get_riders_for_horse`: AJAX endpoint for dynamic rider selection

### Session Management
Uses Django sessions (no traditional user accounts) - riders identified by `rider_id` in session.

### Image Handling
- Uses Pillow for image processing
- Uploads stored in `/media/journal_images/`
- Configure S3 or similar for production

## Next Steps

1. **Create Michelle's Interface**: Build dedicated dashboard for Michelle to see alerts
2. **Email Notifications**: Send email when rider alerts Michelle
3. **Testing**: Write unit tests for models and views
4. **Production Settings**: Prepare for DigitalOcean deployment
5. **Additional Features**: Consider edit/delete capabilities, export features

---
**Last Updated**: January 9, 2026
