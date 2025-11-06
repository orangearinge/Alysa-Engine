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
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:root@localhost:8889/alysa-db')
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

class UserAttempt(db.Model):
    __tablename__ = 'user_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_title = db.Column(db.Text, nullable=False)
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
    
    print("\n✅ Database initialization completed successfully!")
    print("\nNext steps:")
    print("1. Update your .env file with correct database credentials")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the application: python app.py")

if __name__ == "__main__":
    main()
