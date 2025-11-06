from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import bcrypt
import os
import json
from PIL import Image
import io
import base64

# Import AI models
import sys
import importlib.util

# Import feedback-model-alysa.py
spec_alysa = importlib.util.spec_from_file_location("feedback_model_alysa", "feedback-model-alysa.py")
feedback_model_alysa = importlib.util.module_from_spec(spec_alysa)
spec_alysa.loader.exec_module(feedback_model_alysa)
alysa_feedback = feedback_model_alysa.ai_toefl_feedback

# Import feedback-model-gemini.py
spec_gemini = importlib.util.spec_from_file_location("feedback_model_gemini", "feedback-model-gemini.py")
feedback_model_gemini = importlib.util.module_from_spec(spec_gemini)
spec_gemini.loader.exec_module(feedback_model_gemini)
gemini_feedback = feedback_model_gemini.ai_toefl_feedback

from ocr import process_image

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:root@localhost:8889/alysa')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app)

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attempts = db.relationship('UserAttempt', backref='user', lazy=True)
    test_sessions = db.relationship('TestSession', backref='user', lazy=True)
    ocr_translations = db.relationship('OCRTranslation', backref='user', lazy=True)

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

# Hardcoded questions for learning and test modes
LEARNING_QUESTIONS = [
    {
        "id": 1,
        "title": "Describe Your Hometown",
        "prompt": "Describe your hometown and explain what makes it special. Include details about the culture, food, and people."
    },
    {
        "id": 2,
        "title": "Technology and Education",
        "prompt": "Do you think technology has improved education? Give specific examples and explain your reasoning."
    },
    {
        "id": 3,
        "title": "Environmental Protection",
        "prompt": "What can individuals do to protect the environment? Discuss at least three specific actions."
    }
]

TEST_QUESTIONS = [
    {
        "id": 1,
        "title": "University Life",
        "prompt": "Some students prefer to study alone, while others prefer group study. Which do you prefer and why?"
    },
    {
        "id": 2,
        "title": "Work Experience",
        "prompt": "Do you think students should work part-time while studying? Explain your opinion with examples."
    },
    {
        "id": 3,
        "title": "Social Media Impact",
        "prompt": "How has social media changed the way people communicate? Discuss both positive and negative effects."
    },
    {
        "id": 4,
        "title": "Travel Benefits",
        "prompt": "What are the benefits of traveling to different countries? Give specific examples from your experience or knowledge."
    },
    {
        "id": 5,
        "title": "Future Career",
        "prompt": "Describe your ideal job and explain what steps you are taking to achieve this career goal."
    },
    {
        "id": 6,
        "title": "Health and Lifestyle",
        "prompt": "What habits do you think are important for maintaining good health? Explain why these habits are beneficial."
    },
    {
        "id": 7,
        "title": "Cultural Differences",
        "prompt": "How can understanding cultural differences help in international business? Provide specific examples."
    },
    {
        "id": 8,
        "title": "Online Learning",
        "prompt": "Compare online learning with traditional classroom learning. Which is more effective and why?"
    },
    {
        "id": 9,
        "title": "City vs Rural Life",
        "prompt": "Would you prefer to live in a big city or a small town? Explain your choice with specific reasons."
    },
    {
        "id": 10,
        "title": "Innovation and Change",
        "prompt": "How do you think artificial intelligence will change our daily lives in the next 10 years?"
    }
]

# Helper functions
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        hashed_password = hash_password(data['password'])
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hashed_password
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=new_user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Missing username or password'}), 400
        
        # Find user
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not check_password(data['password'], user.password_hash):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Learning Mode Routes
@app.route('/api/learning/questions', methods=['GET'])
@jwt_required()
def get_learning_questions():
    return jsonify({'questions': LEARNING_QUESTIONS}), 200

@app.route('/api/learning/submit', methods=['POST'])
@jwt_required()
def submit_learning_answer():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('question_id') or not data.get('answer'):
            return jsonify({'error': 'Missing question_id or answer'}), 400
        
        # Find question
        question = next((q for q in LEARNING_QUESTIONS if q['id'] == data['question_id']), None)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        # Get AI feedback based on model choice
        model_choice = data.get('model', 'alysa')  # default to alysa
        
        if model_choice == 'gemini':
            feedback_result = gemini_feedback(data['answer'])
        else:
            feedback_result = alysa_feedback(data['answer'])
        
        # Save attempt to database
        attempt = UserAttempt(
            user_id=user_id,
            question_title=question['title'],
            user_input=data['answer'],
            ai_feedback=json.dumps(feedback_result),
            score=feedback_result.get('score', 0)
        )
        
        db.session.add(attempt)
        db.session.commit()
        
        return jsonify({
            'message': 'Answer submitted successfully',
            'feedback': feedback_result,
            'attempt_id': attempt.id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Test Simulation Routes
@app.route('/api/test/start', methods=['POST'])
@jwt_required()
def start_test_session():
    try:
        user_id = get_jwt_identity()
        
        # Create new test session
        test_session = TestSession(
            user_id=user_id,
            total_score=0.0,
            ai_feedback='Test in progress'
        )
        
        db.session.add(test_session)
        db.session.commit()
        
        return jsonify({
            'message': 'Test session started',
            'session_id': test_session.id,
            'questions': TEST_QUESTIONS,
            'time_limit': 3600  # 60 minutes in seconds
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test/submit', methods=['POST'])
@jwt_required()
def submit_test_answers():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('session_id') or not data.get('answers'):
            return jsonify({'error': 'Missing session_id or answers'}), 400
        
        # Find test session
        session = TestSession.query.filter_by(id=data['session_id'], user_id=user_id).first()
        if not session:
            return jsonify({'error': 'Test session not found'}), 404
        
        total_score = 0
        feedback_summary = []
        
        # Process each answer
        for answer_data in data['answers']:
            question_id = answer_data.get('question_id')
            answer_text = answer_data.get('answer')
            
            if not question_id or not answer_text:
                continue
            
            # Find question
            question = next((q for q in TEST_QUESTIONS if q['id'] == question_id), None)
            if not question:
                continue
            
            # Get AI feedback using Gemini for test mode
            feedback_result = gemini_feedback(answer_text)
            score = feedback_result.get('score', 0)
            total_score += score
            
            # Save individual attempt
            attempt = UserAttempt(
                user_id=user_id,
                question_title=question['title'],
                user_input=answer_text,
                ai_feedback=json.dumps(feedback_result),
                score=score
            )
            db.session.add(attempt)
            
            feedback_summary.append({
                'question': question['title'],
                'score': score,
                'feedback': feedback_result.get('feedback', [])
            })
        
        # Calculate average score
        num_questions = len(data['answers'])
        average_score = total_score / num_questions if num_questions > 0 else 0
        
        # Generate overall feedback
        overall_feedback = f"Test completed with average score: {average_score:.2f}/5.0"
        if average_score >= 4.0:
            overall_feedback += " - Excellent performance! You demonstrate strong TOEFL writing skills."
        elif average_score >= 3.0:
            overall_feedback += " - Good performance with room for improvement in grammar and coherence."
        else:
            overall_feedback += " - Needs improvement. Focus on grammar, vocabulary, and essay structure."
        
        # Update test session
        session.total_score = average_score
        session.ai_feedback = json.dumps({
            'overall_feedback': overall_feedback,
            'detailed_feedback': feedback_summary
        })
        session.finished_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Test completed successfully',
            'total_score': average_score,
            'overall_feedback': overall_feedback,
            'detailed_feedback': feedback_summary
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# OCR Translation Routes
@app.route('/api/ocr/translate', methods=['POST'])
@jwt_required()
def ocr_translate():
    try:
        user_id = get_jwt_identity()
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Process image
        image = Image.open(file.stream)
        result = process_image(image)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        # Save OCR result to database
        ocr_record = OCRTranslation(
            user_id=user_id,
            original_text=result.get('detected_language', '') + ': ' + str(result),
            translated_and_explained=json.dumps(result)
        )
        
        db.session.add(ocr_record)
        db.session.commit()
        
        return jsonify({
            'message': 'OCR translation completed',
            'result': result,
            'record_id': ocr_record.id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User History Routes
@app.route('/api/user/attempts', methods=['GET'])
@jwt_required()
def get_user_attempts():
    try:
        user_id = get_jwt_identity()
        attempts = UserAttempt.query.filter_by(user_id=user_id).order_by(UserAttempt.created_at.desc()).all()
        
        attempts_data = []
        for attempt in attempts:
            attempts_data.append({
                'id': attempt.id,
                'question_title': attempt.question_title,
                'score': attempt.score,
                'created_at': attempt.created_at.isoformat(),
                'feedback': json.loads(attempt.ai_feedback) if attempt.ai_feedback else {}
            })
        
        return jsonify({'attempts': attempts_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/test-sessions', methods=['GET'])
@jwt_required()
def get_user_test_sessions():
    try:
        user_id = get_jwt_identity()
        sessions = TestSession.query.filter_by(user_id=user_id).order_by(TestSession.started_at.desc()).all()
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': session.id,
                'total_score': session.total_score,
                'started_at': session.started_at.isoformat(),
                'finished_at': session.finished_at.isoformat() if session.finished_at else None,
                'feedback': json.loads(session.ai_feedback) if session.ai_feedback else {}
            })
        
        return jsonify({'test_sessions': sessions_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/ocr-history', methods=['GET'])
@jwt_required()
def get_user_ocr_history():
    try:
        user_id = get_jwt_identity()
        ocr_records = OCRTranslation.query.filter_by(user_id=user_id).order_by(OCRTranslation.created_at.desc()).all()
        
        ocr_data = []
        for record in ocr_records:
            ocr_data.append({
                'id': record.id,
                'original_text': record.original_text,
                'result': json.loads(record.translated_and_explained) if record.translated_and_explained else {},
                'created_at': record.created_at.isoformat()
            })
        
        return jsonify({'ocr_history': ocr_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check route
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'TOEFL Learning API is running'}), 200

if __name__ == '__main__':
    # Initialize database tables
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
