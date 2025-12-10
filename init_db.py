#!/usr/bin/env python3
"""
Database initialization script for TOEFL Learning System
Run this script to create the database and tables
"""

from urllib.parse import urlparse
import pymysql
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config import Config

# Load environment variables

# Create a minimal Flask app for database initialization
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS

db = SQLAlchemy(app)

# Database Models (copied from app.py to avoid import issues)
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
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
        uri = Config.SQLALCHEMY_DATABASE_URI
        parsed = urlparse(uri)
        
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host=parsed.hostname,
            port=parsed.port,
            user=parsed.username,
            password=parsed.password,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
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
    """Populate tables with sample learning questions and TOEFL iBT test questions (6 tasks)"""
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
            
            # TOEFL iBT Test Questions - 6 Tasks (4 Speaking + 2 Writing)
            test_questions = [
                # Speaking Task 1 - Independent
                {
                    "section": "speaking",
                    "task_type": "independent",
                    "prompt": "Some people prefer to live in a small town, while others prefer to live in a big city. Which do you prefer and why? Use specific reasons and examples to support your answer.",
                    "reference_answer": "I prefer living in a big city because of the opportunities and convenience it offers...",
                    "keywords": '["city", "town", "preference", "opportunities", "lifestyle"]'
                },
                # Speaking Task 2 - Integrated (Campus Situation)
                {
                    "section": "speaking",
                    "task_type": "integrated",
                    "prompt": "The university is planning to build a new student recreation center. Read the announcement and listen to the conversation between two students. Then explain the woman's opinion about the plan and the reasons she gives.",
                    "reference_answer": "The woman supports the new recreation center because it will provide better facilities for students...",
                    "keywords": '["recreation center", "university", "student opinion", "facilities", "campus"]'
                },
                # Speaking Task 3 - Integrated (Academic Course)
                {
                    "section": "speaking",
                    "task_type": "integrated",
                    "prompt": "Read the passage about behavioral economics and listen to the professor's lecture. Explain how the example used by the professor illustrates the concept described in the reading.",
                    "reference_answer": "The professor uses the example of consumer choice to demonstrate how behavioral economics differs from traditional economic theory...",
                    "keywords": '["behavioral economics", "professor", "example", "consumer choice", "theory"]'
                },
                # Speaking Task 4 - Integrated (Academic Lecture)
                {
                    "section": "speaking",
                    "task_type": "integrated",
                    "prompt": "Listen to part of a lecture in a biology class about animal adaptation. Using points and examples from the lecture, explain how animals adapt to extreme environments.",
                    "reference_answer": "The professor explains that animals adapt to extreme environments through various mechanisms such as physical changes and behavioral modifications...",
                    "keywords": '["animal adaptation", "extreme environments", "biology", "mechanisms", "survival"]'
                },
                # Writing Task 1 - Integrated
                {
                    "section": "writing",
                    "task_type": "integrated",
                    "prompt": "Summarize the points made in the lecture, being sure to explain how they cast doubt on the specific points made in the reading passage about the benefits of working from home.",
                    "reference_answer": "The reading passage argues that working from home provides numerous benefits including increased productivity and better work-life balance. However, the lecture challenges these claims...",
                    "keywords": '["working from home", "benefits", "productivity", "work-life balance", "challenges"]'
                },
                # Writing Task 2 - Independent
                {
                    "section": "writing",
                    "task_type": "independent",
                    "prompt": "Do you agree or disagree with the following statement? It is more important for students to understand ideas and concepts than it is for them to learn facts. Use specific reasons and examples to support your answer.",
                    "reference_answer": "I agree that understanding ideas and concepts is more important than memorizing facts. In today's information age, students need critical thinking skills...",
                    "keywords": '["education", "concepts", "facts", "critical thinking", "learning"]'
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
            print(f"Inserted {len(learning_questions)} learning questions and {len(test_questions)} TOEFL iBT test questions")
            print("TOEFL iBT Test Structure:")
            print("  - 4 Speaking Tasks (1 Independent + 3 Integrated)")
            print("  - 2 Writing Tasks (1 Integrated + 1 Independent)")
            print("  - Total: 6 individual tasks for complete evaluation")
            
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
