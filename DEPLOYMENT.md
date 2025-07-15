# Deployment Guide for Funda Educational Platform

## Overview
This document provides deployment instructions for the Funda educational platform on various platforms including Render, Heroku, and Railway.

## Prerequisites
- Python 3.11+
- PostgreSQL database
- Git repository

## Environment Variables
The following environment variables are required:

- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Secret key for session management (auto-generated on Render)
- `PORT`: Port number (automatically set by hosting platform)
- `LOG_LEVEL`: Logging level (optional, defaults to INFO)
- `DEBUG`: Debug mode (optional, defaults to False)

## Deployment on Render

### 1. Repository Setup
1. Push your code to GitHub
2. Connect your GitHub repository to Render

### 2. Database Setup
1. Create a PostgreSQL database on Render
2. Note the database connection string

### 3. Web Service Configuration
- **Environment**: Python 3
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 1 main:app`
- **Auto-Deploy**: Yes

### 4. Environment Variables
Set the following in Render dashboard:
- `DATABASE_URL`: Link to your PostgreSQL database
- `SESSION_SECRET`: Generate a random secret
- `LOG_LEVEL`: INFO (optional)

## Deployment on Heroku

### 1. Install Heroku CLI
```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh
```

### 2. Create Heroku App
```bash
heroku create your-app-name
```

### 3. Add PostgreSQL Add-on
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

### 4. Set Environment Variables
```bash
heroku config:set SESSION_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set LOG_LEVEL=INFO
```

### 5. Deploy
```bash
git push heroku main
```

## Deployment on Railway

### 1. Connect Repository
1. Go to Railway dashboard
2. Connect your GitHub repository

### 2. Add PostgreSQL Database
1. Add PostgreSQL service
2. Note the connection variables

### 3. Environment Variables
Set in Railway dashboard:
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Random secret key

## Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export DATABASE_URL="postgresql://user:password@localhost/funda"
export SESSION_SECRET="your-secret-key"
export DEBUG="True"
```

### 3. Initialize Database
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 4. Run Application
```bash
python main.py
```

## Common Issues and Solutions

### Database Connection Issues
- Ensure `DATABASE_URL` is correctly set
- Check if the database service is running
- Verify database credentials

### Missing Dependencies
- Ensure all dependencies are listed in `requirements.txt`
- Check Python version compatibility

### File Upload Issues
- Ensure upload directories exist
- Check file permissions
- Verify file size limits

### Session Issues
- Ensure `SESSION_SECRET` is set
- Use a strong, random secret key
- Don't use the default development key in production

## Security Considerations

1. **Never commit sensitive data** like API keys or database credentials
2. **Use environment variables** for all configuration
3. **Set secure session secrets** in production
4. **Enable HTTPS** on your hosting platform
5. **Regular security updates** for dependencies

## File Structure for Deployment
```
funda/
├── app.py                 # Application factory
├── main.py               # Main application entry point
├── models.py             # Database models
├── forms.py              # WTForms definitions
├── templates/            # Jinja2 templates
├── static/              # Static files (CSS, JS, images)
├── uploads/             # Video uploads (created automatically)
├── requirements.txt     # Python dependencies
├── runtime.txt          # Python version
├── Procfile            # Process definitions
├── build.sh            # Build script
├── render.yaml         # Render configuration
└── .gitignore          # Git ignore rules
```

## Database Schema
The application automatically creates the following tables:
- `user`: User accounts and profiles
- `comment`: Student-teacher communications
- `voice_note`: Audio file uploads
- `homework_request`: Student homework requests
- `notification`: System notifications

## Monitoring and Maintenance

### Health Check
- Default health check endpoint: `/`
- Monitor application logs for errors
- Check database connection status

### Backup Strategy
- Regular database backups
- File upload backups
- Configuration backup

### Performance Monitoring
- Monitor response times
- Check database query performance
- Monitor resource usage

## Support
For deployment issues, check:
1. Application logs
2. Database connection
3. Environment variables
4. File permissions
5. Dependencies installation