#!/usr/bin/env python3
"""
Database initialization script for TOEFL Learning System
This script ONLY:
- Creates database (if not exists)
- Creates tables (EMPTY, no seed data)

Safe for production / VBox
"""

from urllib.parse import urlparse
from datetime import datetime

import pymysql
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Config

# -------------------------------------------------------------------
# Minimal Flask App for DB Initialization
# -------------------------------------------------------------------

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = Config.SQLALCHEMY_TRACK_MODIFICATIONS

db = SQLAlchemy(app)

# -------------------------------------------------------------------
# Database Models
# -------------------------------------------------------------------

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Profile
    target_score = db.Column(db.Float, default=6.5)
    daily_study_time_minutes = db.Column(db.Integer, default=30)
    test_date = db.Column(db.DateTime)

    attempts = db.relationship("UserAttempt", backref="user", lazy=True, cascade="all, delete-orphan")
    test_sessions = db.relationship("TestSession", backref="user", lazy=True, cascade="all, delete-orphan")
    ocr_translations = db.relationship("OCRTranslation", backref="user", lazy=True, cascade="all, delete-orphan")
    lesson_progress = db.relationship("UserLessonProgress", backref="user", lazy=True, cascade="all, delete-orphan")
    feedbacks = db.relationship("UserFeedback", backref="user", lazy=True, cascade="all, delete-orphan")


class Lesson(db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    duration_minutes = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sections = db.relationship(
        "LessonSection",
        backref="lesson",
        lazy=True,
        cascade="all, delete-orphan"
    )


class LessonSection(db.Model):
    __tablename__ = "lesson_sections"

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.String(50), db.ForeignKey("lessons.id"), nullable=False)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, default="")
    quiz_id = db.Column(db.String(50), db.ForeignKey("quizzes.id"), nullable=True)


class Quiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.Text, nullable=False)

    questions = db.relationship(
        "QuizQuestion",
        backref="quiz",
        lazy=True,
        cascade="all, delete-orphan"
    )


class QuizQuestion(db.Model):
    __tablename__ = "quiz_questions"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.String(50), db.ForeignKey("quizzes.id"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text)
    correct_option_index = db.Column(db.Integer)


class UserLessonProgress(db.Model):
    __tablename__ = "user_lesson_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id = db.Column(db.String(50), db.ForeignKey("lessons.id"), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    last_accessed_at = db.Column(db.DateTime, default=datetime.utcnow)


class LearningQuestion(db.Model):
    __tablename__ = "learning_questions"

    id = db.Column(db.Integer, primary_key=True)
    skill_type = db.Column(db.Text, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    reference_answer = db.Column(db.Text)
    keywords = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attempts = db.relationship("UserAttempt", backref="learning_question", lazy=True)


class TestQuestion(db.Model):
    __tablename__ = "test_questions"

    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.Text, nullable=False)
    task_type = db.Column(db.Text, nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    reference_answer = db.Column(db.Text)
    keywords = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserAttempt(db.Model):
    __tablename__ = "user_attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    learning_question_id = db.Column(
        db.Integer,
        db.ForeignKey("learning_questions.id"),
        nullable=True
    )
    question_type = db.Column(db.String(50))
    question_id = db.Column(db.String(50))
    user_input = db.Column(db.Text, nullable=False)
    ai_feedback = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TestSession(db.Model):
    __tablename__ = "test_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total_score = db.Column(db.Float, nullable=False)
    ai_feedback = db.Column(db.Text, nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)

    test_answers = db.relationship("TestAnswer", backref="test_session", lazy=True, cascade="all, delete-orphan")


class TestAnswer(db.Model):
    __tablename__ = "test_answers"

    id = db.Column(db.Integer, primary_key=True)
    test_session_id = db.Column(
        db.Integer,
        db.ForeignKey("test_sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    section = db.Column(db.Text, nullable=False)
    task_type = db.Column(db.Text, nullable=False)
    combined_question_ids = db.Column(db.Text, nullable=False)
    user_inputs = db.Column(db.Text, nullable=False)
    ai_feedback = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class OCRTranslation(db.Model):
    __tablename__ = "ocr_translations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    translated_and_explained = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserFeedback(db.Model):
    __tablename__ = "user_feedback"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    feedback_text = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# -------------------------------------------------------------------
# Initialization Functions
# -------------------------------------------------------------------

def create_database():
    """Create database if it does not exist"""
    try:
        uri = Config.SQLALCHEMY_DATABASE_URI
        parsed = urlparse(uri)

        connection = pymysql.connect(
            host=parsed.hostname,
            port=parsed.port or 3306,
            user=parsed.username,
            password=parsed.password,
            charset="utf8mb4"
        )

        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                CREATE DATABASE IF NOT EXISTS `{parsed.path[1:]}`
                CHARACTER SET utf8mb4
                COLLATE utf8mb4_unicode_ci
                """
            )

        connection.commit()
        connection.close()
        print(f"✅ Database '{parsed.path[1:]}' ready")

    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False

    return True


def create_tables():
    """Create all tables"""
    try:
        with app.app_context():
            db.create_all()

            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()

            print("✅ Tables created:")
            for table in tables:
                print(f"   - {table}")

    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

    return True


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main():
    print("🚀 Initializing Database (EMPTY TABLES MODE)")

    if not create_database():
        return

    if not create_tables():
        return

    print("\n🎉 Database initialization completed (no seed data)")


if __name__ == "__main__":
    main()
