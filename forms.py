from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, SelectField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('student', 'Student'), ('teacher', 'Teacher')], validators=[DataRequired()])
    grade = SelectField('Grade (Students only)', choices=[(str(i), f'Grade {i}') for i in range(1, 13)], coerce=str)
    subjects = StringField('Subjects (Teachers only - comma separated)', description='e.g., Math, Science, English')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class CommentForm(FlaskForm):
    content = TextAreaField('Write a message to your teacher...', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Send Comment')

class HomeworkRequestForm(FlaskForm):
    content = TextAreaField('What homework do you have or what do you want to learn?', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Send Request')

class VoiceNoteForm(FlaskForm):
    voice_note = FileField('Upload Voice Note', validators=[
        FileRequired(),
        FileAllowed(['mp3', 'wav', 'ogg', 'm4a', 'aac'], 'Audio files only!')
    ])
    submit = SubmitField('Upload Voice Note')

class VideoUploadForm(FlaskForm):
    file = FileField('Choose Video File', validators=[
        FileRequired(),
        FileAllowed(['mp4', 'avi', 'mov', 'mkv', 'webm'], 'Video files only!')
    ])
    grade = HiddenField('Grade')
    subject = HiddenField('Subject')
    submit = SubmitField('Upload Video')

class HomeworkResponseForm(FlaskForm):
    response = TextAreaField('Response', validators=[DataRequired(), Length(max=1000)])
    status = SelectField('Status', choices=[('pending', 'Pending'), ('completed', 'Completed'), ('rejected', 'Rejected')])
    submit = SubmitField('Update')