import os
import logging
from flask import render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.utils import secure_filename
from app import app, db, GRADES, SUBJECTS, allowed_file, allowed_audio_file
from models import User, Comment, VoiceNote, HomeworkRequest, Notification
from forms import LoginForm, RegistrationForm, CommentForm, HomeworkRequestForm, VoiceNoteForm, VideoUploadForm, HomeworkResponseForm
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            name=form.name.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        
        if form.role.data == 'student':
            user.grade = int(form.grade.data) if form.grade.data else None
        elif form.role.data == 'teacher':
            user.subjects = form.subjects.data
        
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard."""
    if current_user.is_student():
        # Show available teachers for students
        teachers = User.query.filter_by(role='teacher').all()
        return render_template('student_dashboard.html', teachers=teachers)
    elif current_user.is_teacher():
        # Show notifications and homework requests for teachers
        notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
        homework_requests = HomeworkRequest.query.filter_by(teacher_id=current_user.id).order_by(HomeworkRequest.created_at.desc()).all()
        return render_template('teacher_dashboard.html', notifications=notifications, homework_requests=homework_requests)
    else:
        return redirect(url_for('index'))

# Interactive Features Routes
@app.route('/interact/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def interact(teacher_id):
    """Student interaction with teacher."""
    if not current_user.is_student():
        flash('Only students can interact with teachers.', 'error')
        return redirect(url_for('dashboard'))
    
    teacher = User.query.get_or_404(teacher_id)
    if not teacher.is_teacher():
        flash('User is not a teacher.', 'error')
        return redirect(url_for('dashboard'))
    
    # Handle form submissions
    if request.method == 'POST':
        # Comment submission
        comment_text = request.form.get('comment')
        if comment_text:
            comment = Comment(content=comment_text, author_id=current_user.id, target_id=teacher.id)
            db.session.add(comment)
            notification = Notification(
                message=f"{current_user.name} commented: {comment_text[:50]}...",
                user_id=teacher.id,
                notification_type='comment'
            )
            db.session.add(notification)
        
        # Homework request submission
        homework_text = request.form.get('homework_request')
        if homework_text:
            homework_request = HomeworkRequest(
                content=homework_text,
                learner_id=current_user.id,
                teacher_id=teacher.id
            )
            db.session.add(homework_request)
            notification = Notification(
                message=f"{current_user.name} sent a homework request",
                user_id=teacher.id,
                notification_type='homework'
            )
            db.session.add(notification)
        
        # Voice note upload
        if 'voice_note' in request.files:
            file = request.files['voice_note']
            if file and file.filename and allowed_audio_file(file.filename):
                # Generate unique filename
                filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                filepath = os.path.join(app.config['VOICE_NOTES_FOLDER'], filename)
                file.save(filepath)
                
                voice_note = VoiceNote(
                    filename=filename,
                    original_filename=file.filename,
                    learner_id=current_user.id
                )
                db.session.add(voice_note)
                notification = Notification(
                    message=f"{current_user.name} sent a voice note",
                    user_id=teacher.id,
                    notification_type='voice_note'
                )
                db.session.add(notification)
        
        db.session.commit()
        flash("Message sent to teacher successfully!", 'success')
        return redirect(url_for('interact', teacher_id=teacher_id))
    
    # Get previous comments and interactions
    comments = Comment.query.filter_by(author_id=current_user.id, target_id=teacher.id).order_by(Comment.created_at.desc()).all()
    homework_requests = HomeworkRequest.query.filter_by(learner_id=current_user.id, teacher_id=teacher.id).order_by(HomeworkRequest.created_at.desc()).all()
    voice_notes = VoiceNote.query.filter_by(learner_id=current_user.id).order_by(VoiceNote.created_at.desc()).all()
    
    return render_template('interaction.html', 
                         teacher=teacher, 
                         comments=comments, 
                         homework_requests=homework_requests,
                         voice_notes=voice_notes)

@app.route('/notifications')
@login_required
def notifications():
    """View notifications."""
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifications)

@app.route('/mark_notification_read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('notifications'))
    
    notification.is_read = True
    db.session.commit()
    return redirect(url_for('notifications'))

@app.route('/homework_requests')
@login_required
def homework_requests():
    """View homework requests (for teachers)."""
    if not current_user.is_teacher():
        flash('Only teachers can view homework requests.', 'error')
        return redirect(url_for('dashboard'))
    
    requests = HomeworkRequest.query.filter_by(teacher_id=current_user.id).order_by(HomeworkRequest.created_at.desc()).all()
    return render_template('homework_requests.html', requests=requests)

@app.route('/respond_homework/<int:request_id>', methods=['GET', 'POST'])
@login_required
def respond_homework(request_id):
    """Respond to homework request."""
    if not current_user.is_teacher():
        flash('Only teachers can respond to homework requests.', 'error')
        return redirect(url_for('dashboard'))
    
    homework_request = HomeworkRequest.query.get_or_404(request_id)
    if homework_request.teacher_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('homework_requests'))
    
    form = HomeworkResponseForm()
    if form.validate_on_submit():
        homework_request.response = form.response.data
        homework_request.status = form.status.data
        homework_request.updated_at = datetime.utcnow()
        
        # Notify student
        notification = Notification(
            message=f"Teacher responded to your homework request: {form.response.data[:50]}...",
            user_id=homework_request.learner_id,
            notification_type='homework'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Response sent successfully!', 'success')
        return redirect(url_for('homework_requests'))
    
    form.response.data = homework_request.response
    form.status.data = homework_request.status
    return render_template('respond_homework.html', form=form, request=homework_request)

@app.route('/voice_note/<filename>')
@login_required
def serve_voice_note(filename):
    """Serve voice note files."""
    return send_from_directory(app.config['VOICE_NOTES_FOLDER'], filename)

def get_uploaded_videos(grade, subject):
    """Get list of uploaded videos for a specific grade and subject."""
    videos = []
    subject_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'grade_{grade}', subject.lower().replace(' ', '_'))
    
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
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html', grades=GRADES)

@app.route('/grade/<int:grade>')
@login_required
def grade_page(grade):
    """Grade page with subject selection."""
    if grade not in GRADES:
        flash('Invalid grade selected.', 'error')
        return redirect(url_for('index'))
    
    return render_template('grade.html', grade=grade, subjects=SUBJECTS)

@app.route('/grade/<int:grade>/subject/<subject>')
@login_required
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
@login_required
def upload_video():
    """Handle video upload."""
    if not current_user.is_teacher():
        flash('Only teachers can upload videos.', 'error')
        return redirect(url_for('dashboard'))
    
    if 'file' not in request.files:
        flash('No file selected.', 'error')
        return redirect(request.referrer or url_for('dashboard'))
    
    file = request.files['file']
    grade = request.form.get('grade')
    subject = request.form.get('subject')
    
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(request.referrer or url_for('dashboard'))
    
    if not grade or not subject:
        flash('Grade and subject are required.', 'error')
        return redirect(request.referrer or url_for('dashboard'))
    
    try:
        grade = int(grade)
        if grade not in GRADES or subject not in SUBJECTS:
            flash('Invalid grade or subject.', 'error')
            return redirect(request.referrer or url_for('dashboard'))
    except ValueError:
        flash('Invalid grade format.', 'error')
        return redirect(request.referrer or url_for('dashboard'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Create directory structure
        subject_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'grade_{grade}', subject.lower().replace(' ', '_'))
        os.makedirs(subject_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(subject_folder, filename)
        file.save(file_path)
        
        flash(f'Video "{filename}" uploaded successfully!', 'success')
        logging.info(f'Video uploaded: {file_path}')
        
        return redirect(url_for('subject_page', grade=grade, subject=subject))
    else:
        flash('Invalid file type. Please upload a video file (mp4, avi, mov, mkv, webm).', 'error')
        return redirect(request.referrer or url_for('dashboard'))

@app.route('/video/<path:filename>')
@login_required
def uploaded_video(filename):
    """Serve uploaded video files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard with system overview."""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))

    users = User.query.all()
    comments = Comment.query.all()
    requests = HomeworkRequest.query.all()
    notifications = Notification.query.all()
    voice_notes = VoiceNote.query.all()
    
    # Get some statistics
    stats = {
        'total_users': len(users),
        'total_students': len([u for u in users if u.role == 'student']),
        'total_teachers': len([u for u in users if u.role == 'teacher']),
        'total_comments': len(comments),
        'total_requests': len(requests),
        'pending_requests': len([r for r in requests if r.status == 'pending']),
        'total_notifications': len(notifications),
        'unread_notifications': len([n for n in notifications if not n.is_read]),
        'total_voice_notes': len(voice_notes)
    }
    
    return render_template('admin.html', 
                         users=users, 
                         comments=comments, 
                         requests=requests,
                         notifications=notifications,
                         voice_notes=voice_notes,
                         stats=stats)

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    flash('File is too large. Maximum size is 500MB.', 'error')
    return redirect(request.referrer or url_for('dashboard'))

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html', grades=GRADES), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
