# Deployment Checklist

## Pre-Deployment (Local)

- [ ] Code committed to git repository
- [ ] All tests passing
- [ ] `.env` file configured for development
- [ ] `requirements.txt` updated with all dependencies
- [ ] README.md updated with deployment info
- [ ] Environment files copied to `deploy/` folder

## Deployment Steps

### Phase 1: SSH & Initial Setup
- [ ] SSH into droplet: `ssh root@143.198.2.6`
- [ ] Verify Ubuntu 22.04: `lsb_release -a`
- [ ] Update system: `apt-get update && apt-get upgrade -y`

### Phase 2: Application Deployment
- [ ] Create `journalapp` user
- [ ] Create `/var/www/journal-app` directory
- [ ] Clone repository
- [ ] Set up Python virtual environment
- [ ] Install Python dependencies

### Phase 3: Database Setup
- [ ] Install PostgreSQL
- [ ] Create database `journal_db`
- [ ] Create database user `journal_user`
- [ ] Grant permissions

### Phase 4: Django Configuration
- [ ] Create `.env.production` file
- [ ] Generate SECRET_KEY
- [ ] Set EMAIL credentials
- [ ] Run migrations
- [ ] Collect static files
- [ ] Create superuser

### Phase 5: Application Server
- [ ] Install Gunicorn
- [ ] Configure systemd service
- [ ] Enable and start journal-app service

### Phase 6: Web Server
- [ ] Install Nginx
- [ ] Copy Nginx configuration
- [ ] Enable site
- [ ] Test Nginx configuration
- [ ] Restart Nginx

### Phase 7: Verification
- [ ] Visit http://143.198.2.6
- [ ] Test rider login
- [ ] Test entry creation
- [ ] Test Michelle's dashboard
- [ ] Test email notification (if configured)

## Post-Deployment

### Security
- [ ] Update SECRET_KEY in `.env.production`
- [ ] Verify DEBUG=False in settings
- [ ] Set secure database password
- [ ] Configure firewall if needed
- [ ] Set up SSL/HTTPS (Optional but recommended)

### Monitoring
- [ ] Set up log rotation
- [ ] Configure email alerts for errors
- [ ] Set up automated backups
- [ ] Test backup restoration

### Documentation
- [ ] Document admin credentials
- [ ] Document database credentials
- [ ] Create runbook for common tasks
- [ ] Set up monitoring/alerting

## Important Files to Update

1. **`.env.production`**
   ```
   SECRET_KEY=<randomly-generated>
   EMAIL_HOST_PASSWORD=<gmail-app-password>
   DATABASE_PASSWORD=<secure-password>
   ```

2. **`/etc/nginx/sites-available/journal-app`**
   - If using a domain, update `server_name`
   - Configure SSL paths if using HTTPS

## Commands for Quick Reference

```bash
# SSH to droplet
ssh root@143.198.2.6

# Run deployment script (if available)
sudo /var/www/journal-app/deploy/deploy.sh

# Manual deployment
chmod +x /var/www/journal-app/deploy/deploy.sh
sudo /var/www/journal-app/deploy/deploy.sh

# Check status after deployment
sudo systemctl status journal-app
sudo systemctl status nginx

# View logs
sudo journalctl -u journal-app -f
tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart journal-app
sudo systemctl restart nginx
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check Gunicorn status: `sudo systemctl status journal-app` |
| Database connection error | Verify PostgreSQL is running: `sudo systemctl status postgresql` |
| Static files not loading | Run `collectstatic --noinput` as journalapp user |
| Email not sending | Check `.env.production` EMAIL credentials |
| Permission denied errors | Verify journalapp user owns `/var/www/journal-app` |

## Rollback Plan

If deployment fails:

1. SSH to droplet
2. Check logs: `sudo journalctl -u journal-app -f`
3. Identify issue
4. Fix configuration
5. Restart service: `sudo systemctl restart journal-app`

If major issues:
- Restore from backup
- Or revert git to previous commit: `git revert <commit-hash>`
- Restart application

## Success Criteria

- ✅ App accessible at http://143.198.2.6
- ✅ Can log in as rider
- ✅ Can create journal entries with text and images
- ✅ Can access Michelle's dashboard
- ✅ Email sends when alerting Michelle
- ✅ No errors in application logs
- ✅ Database is persistent (entries survive service restart)

---

**Deployment Started:** January 10, 2026
**Estimated Duration:** 20-30 minutes
