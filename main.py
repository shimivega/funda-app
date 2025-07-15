import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Data structures
GRADES = list(range(1, 13))
SUBJECTS = ['Math', 'Science', 'English', 'Life Orientation']

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_uploaded_videos(grade, subject):
    """Get list of uploaded videos for a specific grade and subject."""
    videos = []
    subject_folder = os.path.join(UPLOAD_FOLDER, f'grade_{grade}', subject.lower().replace(' ', '_'))
    
    if os.path.exists(subject_folder):
        for filename in os.listdir(subject_folder):
            if allowed_file(filename):
                videos.append({
                    'filename': filename,
                    'title': filename.rsplit('.', 1)[0].replace('_', ' ').title(),
                    'path': os.path.join(f'grade_{grade}', subject.lower().replace(' ', '_'), filename)
                })
    
    return videos

@app.route('/')
def index():
    """Home page with grade selection."""
    return render_template('index.html', grades=GRADES)

@app.route('/grade/<int:grade>')
def grade_page(grade):
    """Grade page with subject selection."""
    if grade not in GRADES:
        flash('Invalid grade selected.', 'error')
        return redirect(url_for('index'))
    
    return render_template('grade.html', grade=grade, subjects=SUBJECTS)

@app.route('/grade/<int:grade>/subject/<subject>')
def subject_page(grade, subject):
    """Subject page with live classes and video content."""
    if grade not in GRADES or subject not in SUBJECTS:
        flash('Invalid grade or subject selected.', 'error')
        return redirect(url_for('index'))
    
    # Get uploaded videos for this grade and subject
    videos = get_uploaded_videos(grade, subject)
    
    # Generate Jitsi Meet room name
    room_name = f'funda-grade{grade}-{subject.lower().replace(" ", "")}'
    
    return render_template('subject.html', 
                         grade=grade, 
                         subject=subject, 
                         videos=videos, 
                         room_name=room_name)

@app.route('/upload', methods=['POST'])
def upload_video():
    """Handle video upload."""
    if 'file' not in request.files:
        flash('No file selected.', 'error')
        return redirect(request.referrer or url_for('index'))
    
    file = request.files['file']
    grade = request.form.get('grade')
    subject = request.form.get('subject')
    
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(request.referrer or url_for('index'))
    
    if not grade or not subject:
        flash('Grade and subject are required.', 'error')
        return redirect(request.referrer or url_for('index'))
    
    try:
        grade = int(grade)
        if grade not in GRADES or subject not in SUBJECTS:
            flash('Invalid grade or subject.', 'error')
            return redirect(request.referrer or url_for('index'))
    except ValueError:
        flash('Invalid grade format.', 'error')
        return redirect(request.referrer or url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Create directory structure
        subject_folder = os.path.join(UPLOAD_FOLDER, f'grade_{grade}', subject.lower().replace(' ', '_'))
        os.makedirs(subject_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(subject_folder, filename)
        file.save(file_path)
        
        flash(f'Video "{filename}" uploaded successfully!', 'success')
        logging.info(f'Video uploaded: {file_path}')
        
        return redirect(url_for('subject_page', grade=grade, subject=subject))
    else:
        flash('Invalid file type. Please upload a video file (mp4, avi, mov, mkv, webm).', 'error')
        return redirect(request.referrer or url_for('index'))

@app.route('/video/<path:filename>')
def uploaded_video(filename):
    """Serve uploaded video files."""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    flash('File is too large. Maximum size is 500MB.', 'error')
    return redirect(request.referrer or url_for('index'))

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return render_template('index.html', grades=GRADES), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
