# Funda Educational Platform - Render Deployment Guide

## Quick Deployment Steps

### 1. Repository Setup
- Push your code to GitHub
- Make sure all files are committed

### 2. Render Dashboard
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository

### 3. Build & Deploy Settings
```
Name: funda-app
Environment: Python 3
Build Command: ./build.sh
Start Command: gunicorn --bind 0.0.0.0:$PORT app:app
```

### 4. Environment Variables
Set these in Render dashboard:
- `DATABASE_URL`: Link to your PostgreSQL database
- `SESSION_SECRET`: Auto-generate or set a random string
- `PYTHON_VERSION`: 3.11.10

### 5. Database Setup
1. Create PostgreSQL database in Render
2. Connect it to your web service
3. Database will auto-populate on first deploy

## File Structure (Ready for Render)
```
├── app.py              # Main Flask application
├── main.py             # Routes and views
├── models.py           # Database models
├── forms.py            # Form definitions
├── wsgi.py             # WSGI entry point
├── requirements.txt    # Python dependencies
├── runtime.txt         # Python version
├── Procfile           # Process definitions
├── build.sh           # Build script
├── render.yaml        # Render configuration
├── templates/         # HTML templates
├── static/           # CSS, JS, images
└── uploads/          # File uploads (auto-created)
```

## Key Features
- ✅ PostgreSQL database ready
- ✅ User authentication system
- ✅ Admin dashboard with security
- ✅ Student-teacher interactions
- ✅ File upload capabilities
- ✅ Live video classes (Jitsi Meet)
- ✅ Responsive design

## Default Accounts
After deployment, create these accounts:
- Admin: admin / admin123
- Teacher: teacher1 / password123  
- Student: student1 / password123

## Troubleshooting
1. **Build fails**: Check that build.sh is executable
2. **Database error**: Ensure DATABASE_URL is set correctly
3. **Import errors**: All dependencies are in requirements.txt
4. **Session issues**: Set SESSION_SECRET environment variable

## Support
- Check Render logs for deployment issues
- All configurations are optimized for Render
- Database auto-initializes on first run