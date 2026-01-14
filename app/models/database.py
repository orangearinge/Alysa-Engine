from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    target_score = db.Column(db.Float, default=6.5)
    daily_study_time_minutes = db.Column(db.Integer, default=30)
    test_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationships
    attempts = db.relationship('UserAttempt', backref='user', lazy=True)
    test_sessions = db.relationship('TestSession', backref='user', lazy=True)
    ocr_translations = db.relationship('OCRTranslation', backref='user', lazy=True)
    lesson_progress = db.relationship('UserLessonProgress', backref='user', lazy=True)

class Lesson(db.Model):
    __tablename__ = 'lessons'
    # Using String ID to match flexible frontend IDs like 's2', '1'
    id = db.Column(db.String(50), primary_key=True) 
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50)) # Speaking, Writing, Reading, Listening
    duration_minutes = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    sections = db.relationship('LessonSection', backref='lesson', lazy=True, cascade="all, delete-orphan")

class LessonSection(db.Model):
    __tablename__ = 'lesson_sections'
    
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.String(50), db.ForeignKey('lessons.id'), nullable=False)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, default='')
    quiz_id = db.Column(db.String(50), db.ForeignKey('quizzes.id'), nullable=True)

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.Text, nullable=False)
    
    questions = db.relationship('QuizQuestion', backref='quiz', lazy=True, cascade="all, delete-orphan")

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.String(50), db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text) # Stored as JSON string: "['Option A', 'Option B']"
    correct_option_index = db.Column(db.Integer)

class UserLessonProgress(db.Model):
    __tablename__ = 'user_lesson_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.String(50), db.ForeignKey('lessons.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    last_accessed_at = db.Column(db.DateTime, default=datetime.now)

# Keeping TestQuestion and related for the "Start Test" feature
class TestQuestion(db.Model):
    __tablename__ = 'test_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.Text, nullable=False)  # 'speaking' or 'writing'
    task_type = db.Column(db.Text, nullable=False)  # 'independent', 'integrated', etc.
    prompt = db.Column(db.Text, nullable=False)
    reference_answer = db.Column(db.Text)  # optional
    keywords = db.Column(db.Text)  # JSON format
    created_at = db.Column(db.DateTime, default=datetime.now)

class UserAttempt(db.Model):
    __tablename__ = 'user_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Changed to flexible question_id or we can link it mainly to Test/Quiz. 
    # For now, keeping legacy structure but making foreign key optional or handled at app level if needed.
    # To avoid errors with existing code that might query this, I'll keep it simple or comment out FK constraint if table dropped.
    # Assuming we might want to track free-form practice too.
    question_type = db.Column(db.String(50)) # 'test', 'quiz', 'practice'
    question_id = db.Column(db.String(50)) 
    user_input = db.Column(db.Text, nullable=False)
    ai_feedback = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class TestSession(db.Model):
    __tablename__ = 'test_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_score = db.Column(db.Float, nullable=False)
    ai_feedback = db.Column(db.Text, nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.now)
    finished_at = db.Column(db.DateTime)
    
    test_answers = db.relationship('TestAnswer', backref='test_session', lazy=True)

class TestAnswer(db.Model):
    __tablename__ = 'test_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    test_session_id = db.Column(db.Integer, db.ForeignKey('test_sessions.id'), nullable=False)
    section = db.Column(db.Text, nullable=False)
    task_type = db.Column(db.Text, nullable=False)
    combined_question_ids = db.Column(db.Text, nullable=False)
    user_inputs = db.Column(db.Text, nullable=False)
    ai_feedback = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class OCRTranslation(db.Model):
    __tablename__ = 'ocr_translations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    translated_and_explained = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
