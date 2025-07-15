# Funda Educational Platform

## Overview

Funda is a Flask-based educational platform designed for grades 1-12. It provides a structured learning environment with live classes, video content management, and organized subject-based navigation. The platform focuses on four core subjects: Math, Science, English, and Life Orientation.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **UI Framework**: Bootstrap 5.3.0 for responsive design
- **Icons**: Font Awesome 6.4.0 for consistent iconography
- **Styling**: Custom CSS with CSS variables for theming
- **Video Integration**: Jitsi Meet for live classes (client-side integration)

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **File Upload**: Werkzeug for secure file handling
- **Session Management**: Flask sessions with configurable secret key
- **Logging**: Python's built-in logging module
- **File Storage**: Local filesystem for video uploads

### Data Structure
- **Grades**: Simple list (1-12)
- **Subjects**: Hardcoded list ['Math', 'Science', 'English', 'Life Orientation']
- **Video Storage**: Hierarchical folder structure (`uploads/grade_{grade}/{subject}/`)

## Key Components

### 1. Navigation System
- **Grade Selection**: Landing page with grade 1-12 buttons
- **Subject Selection**: Grade-specific subject navigation
- **Breadcrumb Navigation**: Hierarchical navigation support

### 2. Video Management
- **Upload System**: Supports MP4, AVI, MOV, MKV, WebM formats
- **File Size Limit**: 500MB maximum per upload
- **Organization**: Videos organized by grade and subject folders
- **Security**: Filename sanitization using `secure_filename`

### 3. Live Classes
- **Integration**: Jitsi Meet embedded for real-time video classes
- **Access**: Subject-specific live class rooms
- **UI**: Responsive video container with join functionality

### 4. User Interface
- **Responsive Design**: Mobile-first approach with Bootstrap
- **Theme**: Educational color scheme (Sea Green primary, Royal Blue secondary)
- **Accessibility**: ARIA labels and semantic HTML structure

## Data Flow

1. **User Entry**: Users start at index page and select grade
2. **Subject Selection**: Grade page displays available subjects
3. **Content Access**: Subject page provides live class and video content
4. **File Upload**: Admin/teacher uploads are stored in structured folders
5. **Video Retrieval**: System scans filesystem for available videos per subject/grade

## External Dependencies

### Frontend Libraries
- **Bootstrap 5.3.0**: UI components and responsive grid
- **Font Awesome 6.4.0**: Icon library
- **Jitsi Meet**: Live video conferencing (client-side)

### Python Packages
- **Flask**: Web framework
- **Werkzeug**: WSGI utilities and file handling
- **Standard Library**: os, logging for system operations

### File System Requirements
- **Upload Directory**: `uploads/` folder with write permissions
- **Structure**: Automatic creation of grade/subject subdirectories

## Deployment Strategy

### Environment Configuration
- **Session Secret**: Environment variable `SESSION_SECRET` (falls back to dev key)
- **Proxy Support**: ProxyFix middleware for reverse proxy deployments
- **Upload Limits**: Configurable file size limits

### File Storage
- **Local Storage**: Files stored in local `uploads/` directory
- **Scalability Note**: Current implementation uses local filesystem (may need cloud storage for production scale)

### Security Considerations
- **File Validation**: Extension and size validation for uploads
- **Filename Sanitization**: Prevents directory traversal attacks
- **Session Security**: Configurable session secret for production

### Production Readiness
- **Logging**: Debug-level logging configured (should be adjusted for production)
- **Error Handling**: Basic Flask error handling
- **Static Files**: Served through Flask (consider CDN for production)

## Development Notes

- The application uses a simple file-based architecture without a database
- Video content is organized hierarchically by grade and subject
- Live classes are integrated through Jitsi Meet's web SDK
- The platform is designed for easy extension with additional subjects or grades
- Current implementation supports basic CRUD operations for video content