#!/usr/bin/env python3
"""
Database initialization script for TOEFL Learning System
Run this script to create the database and tables
"""

import pymysql
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create a minimal Flask app for database initialization
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:root@localhost:8889/alysa')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models (copied from app.py to avoid import issues)
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LearningQuestion(db.Model):
    __tablename__ = 'learning_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    skill_type = db.Column(db.Text, nullable=False)  # 'speaking' or 'writing'
    level = db.Column(db.Integer, nullable=False)  # 1=beginner, 2=intermediate, etc.
    prompt = db.Column(db.Text, nullable=False)
    reference_answer = db.Column(db.Text)  # optional
    keywords = db.Column(db.Text)  # JSON format
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TestQuestion(db.Model):
    __tablename__ = 'test_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.Text, nullable=False)  # 'speaking' or 'writing'
    task_type = db.Column(db.Text, nullable=False)  # 'independent', 'integrated', etc.
    prompt = db.Column(db.Text, nullable=False)
    reference_answer = db.Column(db.Text)  # optional
    keywords = db.Column(db.Text)  # JSON format
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserAttempt(db.Model):
    __tablename__ = 'user_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    learning_question_id = db.Column(db.Integer, db.ForeignKey('learning_questions.id'), nullable=False)
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
    section = db.Column(db.Text, nullable=False)  # 'speaking' or 'writing'
    task_type = db.Column(db.Text, nullable=False)  # 'independent', 'integrated', etc.
    combined_question_ids = db.Column(db.Text, nullable=False)  # JSON format: [1,2,3]
    user_inputs = db.Column(db.Text, nullable=False)  # JSON format: [{"q_id":1,"answer":"..."}]
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

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Database connection parameters
        host = os.getenv('DB_HOST', 'localhost')
        port = int(os.getenv('DB_PORT', '8889'))
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', 'root')
        database_name = os.getenv('DB_NAME', 'alysa')
        
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"Database '{database_name}' created or already exists")
        
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
            # Create all tables
            db.create_all()
            print("All tables created successfully")
            
            # Print table information
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Created tables: {', '.join(tables)}")
            
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False
    
    return True

def populate_sample_data():
    """Populate tables with sample learning and test questions"""
    try:
        with app.app_context():
            # Check if data already exists
            if LearningQuestion.query.first() or TestQuestion.query.first():
                print("Sample data already exists, skipping population")
                return True
            
            # Sample Learning Questions
            learning_questions = [
                {
                    "skill_type": "writing",
                    "level": 1,
                    "prompt": "Describe your hometown and explain what makes it special. Include details about the culture, food, and people.",
                    "reference_answer": "My hometown is a small city with rich cultural heritage...",
                    "keywords": '["hometown", "culture", "food", "people", "special"]'
                },
                {
                    "skill_type": "writing", 
                    "level": 2,
                    "prompt": "Do you think technology has improved education? Give specific examples and explain your reasoning.",
                    "reference_answer": "Technology has significantly improved education through various means...",
                    "keywords": '["technology", "education", "examples", "reasoning", "improvement"]'
                },
                {
                    "skill_type": "writing",
                    "level": 2,
                    "prompt": "What can individuals do to protect the environment? Discuss at least three specific actions.",
                    "reference_answer": "Individuals can protect the environment through recycling, reducing energy consumption...",
                    "keywords": '["environment", "protection", "individuals", "actions", "sustainability"]'
                }
            ]
            
            # Sample Test Questions
            test_questions = [
                {
                    "section": "writing",
                    "task_type": "independent",
                    "prompt": "Some students prefer to study alone, while others prefer group study. Which do you prefer and why?",
                    "reference_answer": "I prefer studying alone because it allows me to focus better...",
                    "keywords": '["study", "alone", "group", "preference", "focus"]'
                },
                {
                    "section": "writing",
                    "task_type": "independent", 
                    "prompt": "Do you think students should work part-time while studying? Explain your opinion with examples.",
                    "reference_answer": "Students should work part-time as it provides valuable experience...",
                    "keywords": '["students", "work", "part-time", "studying", "experience"]'
                },
                {
                    "section": "writing",
                    "task_type": "integrated",
                    "prompt": "Summarize the main points from the reading passage and explain how the lecture supports or contradicts these points.",
                    "reference_answer": "The reading passage outlines several benefits of renewable energy...",
                    "keywords": '["renewable energy", "benefits", "lecture", "reading", "summarize"]'
                }
            ]
            
            # Insert Learning Questions
            for lq_data in learning_questions:
                lq = LearningQuestion(**lq_data)
                db.session.add(lq)
            
            # Insert Test Questions  
            for tq_data in test_questions:
                tq = TestQuestion(**tq_data)
                db.session.add(tq)
            
            db.session.commit()
            print(f"Inserted {len(learning_questions)} learning questions and {len(test_questions)} test questions")
            
    except Exception as e:
        print(f"Error populating sample data: {e}")
        return False
    
    return True

def main():
    """Main initialization function"""
    print("Initializing TOEFL Learning System Database...")
    
    # Step 1: Create database
    if not create_database():
        print("Failed to create database. Exiting.")
        return
    
    # Step 2: Create tables
    if not create_tables():
        print("Failed to create tables. Exiting.")
        return
    
    # Step 3: Populate sample data
    if not populate_sample_data():
        print("Failed to populate sample data. Exiting.")
        return
    
    print("\n✅ Database initialization completed successfully!")
    print("\nNext steps:")
    print("1. Update your .env file with correct database credentials")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the application: python app.py")

if __name__ == "__main__":
    main()
