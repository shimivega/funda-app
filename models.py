from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='student')  # 'student', 'teacher', 'admin'
    grade = db.Column(db.Integer)  # For students
    subjects = db.Column(db.String(200))  # For teachers - comma-separated subjects
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    authored_comments = db.relationship('Comment', foreign_keys='Comment.author_id', backref='author')
    received_comments = db.relationship('Comment', foreign_keys='Comment.target_id', backref='target')
    voice_notes = db.relationship('VoiceNote', backref='learner')
    homework_requests_sent = db.relationship('HomeworkRequest', foreign_keys='HomeworkRequest.learner_id', backref='learner')
    homework_requests_received = db.relationship('HomeworkRequest', foreign_keys='HomeworkRequest.teacher_id', backref='teacher')
    notifications = db.relationship('Notification', backref='user')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_teacher(self):
        return self.role == 'teacher'
    
    def is_student(self):
        return self.role == 'student'
    
    def get_teacher_subjects(self):
        if self.subjects:
            return [s.strip() for s in self.subjects.split(',')]
        return []

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Comment {self.id}: {self.content[:50]}...>'

class VoiceNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    learner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<VoiceNote {self.id}: {self.filename}>'

class HomeworkRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    learner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'rejected'
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<HomeworkRequest {self.id}: {self.content[:50]}...>'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    notification_type = db.Column(db.String(50), default='general')  # 'comment', 'homework', 'voice_note', 'general'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.message}>'