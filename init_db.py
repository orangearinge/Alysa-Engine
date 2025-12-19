#!/usr/bin/env python3
"""
Database initialization script for TOEFL Learning System
Run this script to create the database and tables
"""

from urllib.parse import urlparse
import pymysql
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config import Config

# Create a minimal Flask app for database initialization
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS

db = SQLAlchemy(app)

# --- Database Models ---

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    attempts = db.relationship('UserAttempt', backref='user', lazy=True)
    test_sessions = db.relationship('TestSession', backref='user', lazy=True)
    ocr_translations = db.relationship('OCRTranslation', backref='user', lazy=True)
    lesson_progress = db.relationship('UserLessonProgress', backref='user', lazy=True)
    
    # User Profile Fields
    target_score = db.Column(db.Float, default=6.5)
    daily_study_time_minutes = db.Column(db.Integer, default=30)
    test_date = db.Column(db.DateTime)

class Lesson(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.String(50), primary_key=True) 
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50)) # Speaking, Writing, Reading, Listening
    duration_minutes = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
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
    options = db.Column(db.Text) # Stored as JSON string
    correct_option_index = db.Column(db.Integer)

class UserLessonProgress(db.Model):
    __tablename__ = 'user_lesson_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.String(50), db.ForeignKey('lessons.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    last_accessed_at = db.Column(db.DateTime, default=datetime.utcnow)

class LearningQuestion(db.Model):
    __tablename__ = 'learning_questions'
    id = db.Column(db.Integer, primary_key=True)
    skill_type = db.Column(db.Text, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    reference_answer = db.Column(db.Text)
    keywords = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    attempts = db.relationship('UserAttempt', backref='learning_question', lazy=True)

class TestQuestion(db.Model):
    __tablename__ = 'test_questions'
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.Text, nullable=False)
    task_type = db.Column(db.Text, nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    reference_answer = db.Column(db.Text)
    keywords = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserAttempt(db.Model):
    __tablename__ = 'user_attempts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    learning_question_id = db.Column(db.Integer, db.ForeignKey('learning_questions.id'), nullable=True) # Made nullable for flexibility
    question_type = db.Column(db.String(50)) 
    question_id = db.Column(db.String(50)) 
    user_input = db.Column(db.Text, nullable=False)
    ai_feedback = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TestSession(db.Model):
    __tablename__ = 'test_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_score = db.Column(db.Float, nullable=False)
    ai_feedback = db.Column(db.Text, nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OCRTranslation(db.Model):
    __tablename__ = 'ocr_translations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    translated_and_explained = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- Initialization Functions ---

def create_database():
    """Create the database if it doesn't exist"""
    try:
        uri = Config.SQLALCHEMY_DATABASE_URI
        parsed = urlparse(uri)
        connection = pymysql.connect(
            host=parsed.hostname,
            port=parsed.port,
            user=parsed.username,
            password=parsed.password,
            charset='utf8mb4'
        )
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{parsed.path[1:]}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"Database '{parsed.path[1:]}' created or already exists")
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        return False
    return True

def create_tables():
    """Create all tables using SQLAlchemy"""
    try:
        with app.app_context():
            db.create_all()
            print("All tables created successfully")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Created tables: {', '.join(tables)}")
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False
    return True

def populate_sample_data():
    """Populate tables with sample data"""
    try:
        with app.app_context():
            # Check if Lessons already exist to avoid duplication
            if Lesson.query.first():
                print("Lesson data already exists. Skipping population.")
                return True

            print("Populating Quizzes and Lessons...")

            # 1. Create Quizzes
            q1 = Quiz(id='q1', title='Speaking Basics Quiz')
            db.session.merge(q1)
            
            q1_questions = [
                QuizQuestion(
                    quiz_id='q1',
                    question_text='How many parts are there in the Speaking test?',
                    options=json.dumps(['1', '2', '3', '4']),
                    correct_option_index=2
                ),
                QuizQuestion(
                    quiz_id='q1',
                    question_text='How long does the Speaking test last?',
                    options=json.dumps(['4-5 minutes', '11-14 minutes', '30 minutes', '1 hour']),
                    correct_option_index=1
                )
            ]
            for q in q1_questions:
                 db.session.add(q)

            # 2. Create Lessons
            
            # SPEAKING
            l1 = Lesson(id='1', title='Introduction to IELTS Speaking', description='Learn the basics of the Speaking test format.', category='Speaking', duration_minutes=15)
            db.session.merge(l1)
            l1_sections = [
                LessonSection(lesson_id='1', title='Overview', content='The IELTS Speaking test consists of 3 parts and lasts 11-14 minutes. It is a face-to-face interview with an examiner.'),
                LessonSection(lesson_id='1', title='Part 1: Introduction and Interview', content='In this part, the examiner asks you general questions about yourself...'),
                LessonSection(lesson_id='1', title='Part 2: Long Turn', content='You will be given a card which asks you to talk about a particular topic...'),
                LessonSection(lesson_id='1', title='Quiz: Speaking Basics', quiz_id='q1')
            ]
            
            l2 = Lesson(id='s2', title='Speaking Part 2 Strategies', description='Master the "Long Turn" with effective note-taking.', category='Speaking', duration_minutes=15)
            db.session.merge(l2)
            l2_sections = [
                LessonSection(lesson_id='s2', title='Using the 1 Minute Preparation', content='Don\'t write full sentences. Write keywords and structure your talk.'),
                LessonSection(lesson_id='s2', title='Structure Your Talk', content='Introduction -> Past -> Present -> Future -> Conclusion/Opinion.')
            ]

            l3 = Lesson(id='s3', title='Common Topics in Speaking Part 1', description='Prepare fo questions about home, work, and hobbies.', category='Speaking', duration_minutes=10)
            db.session.merge(l3)
            l3_sections = [
                 LessonSection(lesson_id='s3', title='Home & Hometown', content='Be ready to describe your room, house, or neighborhood.'),
                 LessonSection(lesson_id='s3', title='Work & Studies', content='Know the vocabulary for your major or job role.')
            ]

            l4 = Lesson(id='s4', title='Improving Fluency & Coherence', description='Speak naturally without too many pauses.', category='Speaking', duration_minutes=20)
            db.session.merge(l4)
            l4_sections = [
                 LessonSection(lesson_id='s4', title='Fillers', content='Use natural fillers like "Well...", "Actually...", "To be honest..." instead of "Umm".')
            ]

            # WRITING
            w1 = Lesson(id='2', title='Writing Task 1: Charts', description='How to describe bar charts effectively.', category='Writing', duration_minutes=25)
            db.session.merge(w1)
            w1_sections = [
                 LessonSection(lesson_id='2', title='Understanding Bar Charts', content='Bar charts show comparison between categories.'),
                 LessonSection(lesson_id='2', title='Key Vocabulary', content='Use words like "increase", "decrease", "fluctuate".'),
                 LessonSection(lesson_id='2', title='Quiz: Bar Charts', quiz_id='q1') # Reusing q1 for demo
            ]
            
            w2 = Lesson(id='w2', title='Writing Task 2: Essay Structures', description='Organize your opinion or argument essays clearly.', category='Writing', duration_minutes=30)
            db.session.merge(w2)
            w2_sections = [
                LessonSection(lesson_id='w2', title='4-Paragraph Structure', content='Intro, Body 1, Body 2, Conclusion.'),
                LessonSection(lesson_id='w2', title='Thesis Statement', content='Clearly state your position in the introduction.')
            ]

            w3 = Lesson(id='w3', title='Letter Writing (General Training)', description='Formal vs Informal letters.', category='Writing', duration_minutes=20)
            db.session.merge(w3)
            w3_sections = [
                LessonSection(lesson_id='w3', title='Formal Openings', content='"Dear Sir/Madam,"'),
                LessonSection(lesson_id='w3', title='Informal Openings', content='"Hi John,"')
            ]

            w4 = Lesson(id='w4', title='Vocabulary for Writing', description='Academic words to boost your score.', category='Writing', duration_minutes=15)
            db.session.merge(w4)
            w4_sections = [
                LessonSection(lesson_id='w4', title='Linking Words', content='Furthermore, However, Consequently.')
            ]

            # LISTENING
            li1 = Lesson(id='3', title='Listening for Details', description='Techniques to catch specific information.', category='Listening', duration_minutes=20)
            db.session.merge(li1)
            li1_sections = [
                LessonSection(lesson_id='3', title='Names and Numbers', content='Practice listening for spelling of names and long numbers.')
            ]

            li2 = Lesson(id='l2', title='Predicting Answers', description='Use context to guess the type of word needed.', category='Listening', duration_minutes=20)
            db.session.merge(li2)
            li2_sections = [
                 LessonSection(lesson_id='l2', title='Grammar Clues', content='If there is "a" or "an" before the blank, you know it is a singular noun.')
            ]

            li3 = Lesson(id='l3', title='Listening to Accents', description='Familiarize yourself with British, Australian, and American accents.', category='Listening', duration_minutes=15)
            db.session.merge(li3)
            li3_sections = [
                LessonSection(lesson_id='l3', title='The "R" Sound', content='American English emphasizes the "r".')
            ]

            li4 = Lesson(id='l4', title='Map Labeling', description='Navigating directions in Listening Section 2.', category='Listening', duration_minutes=25)
            db.session.merge(li4)
            li4_sections = [
                LessonSection(lesson_id='l4', title='Directional Language', content='North, South, East, West, across from, next to.')
            ]

            # READING
            r1 = Lesson(id='4', title='Reading Skimming Techniques', description='Read faster and find answers quicker.', category='Reading', duration_minutes=30)
            db.session.merge(r1)
            r1_sections = [
                LessonSection(lesson_id='4', title='Read First and Last Sentences', content='Topic sentences often contain the main idea.')
            ]

            r2 = Lesson(id='r2', title='Scanning for Keywords', description='Locate information without reading every word.', category='Reading', duration_minutes=15)
            db.session.merge(r2)
            r2_sections = [
                LessonSection(lesson_id='r2', title='Proper Nouns and Dates', content='Scan for capital letters and numbers.')
            ]
            
            r3 = Lesson(id='r3', title='True, False, Not Given', description='Strategies to handle this tricky question type.', category='Reading', duration_minutes=25)
            db.session.merge(r3)
            r3_sections = [
                LessonSection(lesson_id='r3', title='Not Given vs False', content='False means the text says the opposite. Not Given means missing info.')
            ]

            r4 = Lesson(id='r4', title='Matching Headings', description='Match the correct heading to paragraphs.', category='Reading', duration_minutes=20)
            db.session.merge(r4)
            r4_sections = [
                 LessonSection(lesson_id='r4', title='Don\'t rely on flexible keywords', content='Focus on the main idea.')
            ]

            # Collect all sections
            all_sections = l1_sections + l2_sections + l3_sections + l4_sections + \
                           w1_sections + w2_sections + w3_sections + w4_sections + \
                           li1_sections + li2_sections + li3_sections + li4_sections + \
                           r1_sections + r2_sections + r3_sections + r4_sections
                           
            for s in all_sections:
                db.session.add(s)

            db.session.commit()
            print("Populated lessons and quizzes.")
            
            # --- Populate legacy questions if needed ---
            if not TestQuestion.query.first():
                 # (Keep your existing standard test questions logic if desired, or skip for brevity if focus is Learning)
                 pass

    except Exception as e:
        print(f"Error populating sample data: {e}")
        db.session.rollback()
        return False
    return True

def main():
    print("Initializing Database...")
    if not create_database(): return
    if not create_tables(): return
    if not populate_sample_data(): return
    print("\n✅ Database initialization completed successfully!")

if __name__ == "__main__":
    main()
