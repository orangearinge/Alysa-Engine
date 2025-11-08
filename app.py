import importlib.util
import json
import os

# Import AI models
from datetime import datetime, timedelta

import bcrypt   
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from PIL import Image

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

class LearningQuestion(db.Model):
    __tablename__ = 'learning_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    skill_type = db.Column(db.Text, nullable=False)  # 'speaking' or 'writing'
    level = db.Column(db.Integer, nullable=False)  # 1=beginner, 2=intermediate, etc.
    prompt = db.Column(db.Text, nullable=False)
    reference_answer = db.Column(db.Text)  # optional
    keywords = db.Column(db.Text)  # JSON format
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attempts = db.relationship('UserAttempt', backref='learning_question', lazy=True)

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
    
    # Relationships
    test_answers = db.relationship('TestAnswer', backref='test_session', lazy=True)

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

# Helper functions for question management
def get_learning_questions_by_level(level=None, skill_type=None):
    """Get learning questions filtered by level and/or skill type"""
    query = LearningQuestion.query
    if level:
        query = query.filter_by(level=level)
    if skill_type:
        query = query.filter_by(skill_type=skill_type)
    return query.all()

def get_test_questions_by_task_type(task_type=None, section=None):
    """Get test questions filtered by task type and/or section"""
    query = TestQuestion.query
    if task_type:
        query = query.filter_by(task_type=task_type)
    if section:
        query = query.filter_by(section=section)
    return query.all()

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
        access_token = create_access_token(identity=str(new_user.id))

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
        access_token = create_access_token(identity=str(user.id))

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
    try:
        # Get query parameters
        level = request.args.get('level', type=int)
        skill_type = request.args.get('skill_type')
        
        # Get questions from database
        questions = get_learning_questions_by_level(level, skill_type)
        
        questions_data = []
        for q in questions:
            questions_data.append({
                'id': q.id,
                'skill_type': q.skill_type,
                'level': q.level,
                'prompt': q.prompt,
                'reference_answer': q.reference_answer,
                'keywords': json.loads(q.keywords) if q.keywords else []
            })
        
        return jsonify({'questions': questions_data}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/learning/submit', methods=['POST'])
@jwt_required()
def submit_learning_answer():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data or not data.get('question_id') or not data.get('answer'):
            return jsonify({'error': 'Missing question_id or answer'}), 400

        # Find question in database
        question = LearningQuestion.query.get(data['question_id'])
        if not question:
            return jsonify({'error': 'Question not found'}), 404

        # Get AI feedback based on model choice
        model_choice = data.get('model', 'alysa')  # default to alysa

        if model_choice == 'gemini':
            feedback_result = gemini_feedback(data['answer'], mode="learning")
        else:
            feedback_result = alysa_feedback(data['answer'])

        # Save attempt to database
        attempt = UserAttempt(
            user_id=user_id,
            learning_question_id=question.id,
            user_input=data['answer'],
            ai_feedback=json.dumps(feedback_result),
            score=feedback_result.get('score', 0)
        )

        db.session.add(attempt)
        db.session.commit()

        return jsonify({
            'message': 'Answer submitted successfully',
            'feedback': feedback_result,
            'attempt_id': attempt.id,
            'question': {
                'id': question.id,
                'prompt': question.prompt,
                'skill_type': question.skill_type,
                'level': question.level
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Test Simulation Routes
@app.route('/api/test/start', methods=['POST'])
@jwt_required()
def start_test_session():
    """
    Start a TOEFL iBT test session with exactly 6 tasks (4 speaking + 2 writing).
    Returns all 6 questions in the proper TOEFL iBT order.
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        
        # TOEFL iBT requires exactly 6 tasks in specific order
        # Get all test questions from database (should be exactly 6)
        all_questions = TestQuestion.query.order_by(TestQuestion.id).all()
        
        if len(all_questions) != 6:
            return jsonify({
                'error': f'TOEFL iBT test requires exactly 6 questions. Found {len(all_questions)} questions in database.'
            }), 500
        
        # Validate that we have the correct TOEFL iBT structure
        expected_structure = [
            {'section': 'speaking', 'task_type': 'independent'},   # Task 1
            {'section': 'speaking', 'task_type': 'integrated'},    # Task 2
            {'section': 'speaking', 'task_type': 'integrated'},    # Task 3
            {'section': 'speaking', 'task_type': 'integrated'},    # Task 4
            {'section': 'writing', 'task_type': 'integrated'},     # Task 5
            {'section': 'writing', 'task_type': 'independent'}     # Task 6
        ]
        
        # Validate question structure
        for i, (question, expected) in enumerate(zip(all_questions, expected_structure)):
            if question.section != expected['section'] or question.task_type != expected['task_type']:
                return jsonify({
                    'error': f'Question {i+1}: Expected {expected["section"]} {expected["task_type"]}, got {question.section} {question.task_type}'
                }), 500
        
        # Create new test session
        test_session = TestSession(
            user_id=user_id,
            total_score=0.0,
            ai_feedback='TOEFL iBT test in progress'
        )

        db.session.add(test_session)
        db.session.commit()
        
        # Format questions for response with task_id
        questions_data = []
        for i, q in enumerate(all_questions):
            questions_data.append({
                'task_id': i + 1,  # TOEFL iBT task numbers 1-6
                'question_id': q.id,
                'section': q.section,
                'task_type': q.task_type,
                'prompt': q.prompt,
                'keywords': json.loads(q.keywords) if q.keywords else []
            })

        return jsonify({
            'message': 'TOEFL iBT test session started',
            'session_id': test_session.id,
            'test_info': {
                'test_type': 'TOEFL iBT Writing & Speaking',
                'total_tasks': 6,
                'task_breakdown': {
                    'speaking_tasks': 4,
                    'writing_tasks': 2
                },
                'time_limit_minutes': 60,
                'scoring_scale': '0-5 points per task'
            },
            'tasks': questions_data,
            'instructions': [
                'Complete all 6 tasks for a full TOEFL iBT evaluation',
                'Each task will be evaluated individually',
                'Speaking tasks: Focus on fluency, clarity, and content development',
                'Writing tasks: Focus on organization, grammar, and idea development',
                'Submit all tasks together when completed'
            ]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test/submit', methods=['POST'])
@jwt_required()
def submit_test_answers():
    """
    Submit TOEFL iBT test answers for evaluation.
    Expects exactly 6 tasks: 4 speaking + 2 writing tasks.
    Each task is evaluated individually using TOEFL iBT rubrics.
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data or not data.get('session_id') or not data.get('task_answers'):
            return jsonify({'error': 'Missing session_id or task_answers'}), 400

        # Find test session
        session = TestSession.query.filter_by(id=data['session_id'], user_id=user_id).first()
        if not session:
            return jsonify({'error': 'Test session not found'}), 404

        task_answers = data.get('task_answers', [])
        
        # Validate that we have exactly 6 tasks for a complete TOEFL iBT test
        if len(task_answers) != 6:
            return jsonify({
                'error': f'TOEFL iBT test requires exactly 6 tasks (4 speaking + 2 writing). Received {len(task_answers)} tasks.'
            }), 400

        total_score = 0
        task_count = 0
        detailed_feedback = []
        
        # Define expected TOEFL iBT task structure
        expected_tasks = [
            {'task_id': 1, 'section': 'speaking', 'task_type': 'independent'},
            {'task_id': 2, 'section': 'speaking', 'task_type': 'integrated'},
            {'task_id': 3, 'section': 'speaking', 'task_type': 'integrated'},
            {'task_id': 4, 'section': 'speaking', 'task_type': 'integrated'},
            {'task_id': 5, 'section': 'writing', 'task_type': 'integrated'},
            {'task_id': 6, 'section': 'writing', 'task_type': 'independent'}
        ]

        # Process each task individually
        for i, task_data in enumerate(task_answers):
            task_id = task_data.get('task_id')
            task_type = task_data.get('task_type')
            section = task_data.get('section')
            answers = task_data.get('answers', [])
            
            # Validate task structure
            if not task_id or not task_type or not section:
                return jsonify({
                    'error': f'Task {i+1}: Missing required fields (task_id, task_type, section)'
                }), 400
            
            if not answers:
                return jsonify({
                    'error': f'Task {task_id}: No answers provided. Each task must have at least one answer.'
                }), 400
            
            # Validate against expected task structure
            expected = expected_tasks[i] if i < len(expected_tasks) else None
            if expected and (task_id != expected['task_id'] or 
                           section != expected['section'] or 
                           task_type != expected['task_type']):
                return jsonify({
                    'error': f'Task {task_id}: Invalid task structure. Expected task_id={expected["task_id"]}, section={expected["section"]}, task_type={expected["task_type"]}'
                }), 400
            
            # Collect question IDs and user inputs for this specific task
            question_ids = []
            user_inputs = []
            combined_text = ""
            
            for answer_item in answers:
                question_id = answer_item.get('question_id')
                answer_text = answer_item.get('answer', '').strip()
                
                if question_id and answer_text:
                    question_ids.append(question_id)
                    user_inputs.append({
                        'q_id': question_id,
                        'answer': answer_text
                    })
                    combined_text += answer_text + " "
            
            if not question_ids:
                return jsonify({
                    'error': f'Task {task_id}: No valid answers found. Each answer must have question_id and non-empty answer text.'
                }), 400
            
            # Evaluate this task individually using test mode
            task_text = combined_text.strip()
            feedback_result = gemini_feedback(task_text, mode="test")
            task_score = feedback_result.get('score', 0)
            
            # Validate score is within expected range
            if not isinstance(task_score, (int, float)) or task_score < 0 or task_score > 5:
                task_score = 0  # Default to 0 if invalid score
            
            total_score += task_score
            task_count += 1
            
            # Save individual test answer record
            test_answer = TestAnswer(
                test_session_id=session.id,
                section=section,
                task_type=task_type,
                combined_question_ids=json.dumps(question_ids),
                user_inputs=json.dumps(user_inputs),
                ai_feedback=json.dumps(feedback_result),
                score=task_score
            )
            db.session.add(test_answer)
            
            # Add to detailed feedback
            detailed_feedback.append({
                'task_id': task_id,
                'task_type': task_type,
                'section': section,
                'score': task_score,
                'feedback': feedback_result.get('feedback', []),
                'question_count': len(question_ids)
            })

        # Calculate overall score (average of all 6 tasks)
        overall_score = total_score / task_count if task_count > 0 else 0

        # TOEFL iBT performance level descriptors (strict format)
        if overall_score >= 5.0:
            performance_level = "Excellent"
        elif overall_score >= 4.0:
            performance_level = "Good"
        elif overall_score >= 3.0:
            performance_level = "Fair"
        elif overall_score >= 2.0:
            performance_level = "Limited"
        elif overall_score >= 1.0:
            performance_level = "Weak"
        else:
            performance_level = "Off-topic"

        # Generate overall feedback
        overall_feedback = f"TOEFL iBT Test Evaluation - Overall Score: {overall_score:.1f}/5.0 - Performance Level: {performance_level}"

        # Update test session
        session.total_score = overall_score
        session.ai_feedback = json.dumps({
            'overall_feedback': overall_feedback,
            'detailed_feedback': detailed_feedback
        })
        session.finished_at = datetime.utcnow()

        db.session.commit()

        # Return strict format response
        return jsonify({
            'message': 'TOEFL iBT Test Evaluation Completed',
            'test_results': {
                'overall_score': round(overall_score, 1),
                'performance_level': performance_level,
                'total_tasks_evaluated': 6,
                'test_type': 'TOEFL iBT Writing & Speaking'
            },
            'evaluation_summary': {
                'overall_feedback': overall_feedback,
                'detailed_task_feedback': detailed_feedback
            },
            'scoring_criteria': {
                'scale': '0-5 points per task',
                'focus_areas': [
                    'Grammar accuracy',
                    'Idea development',
                    'Coherence and organization',
                    'Lexical range',
                    'Task completion'
                ]
            },
            'session_info': {
                'session_id': session.id,
                'completed_at': session.finished_at.isoformat() if session.finished_at else None
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# OCR Translation Routes
@app.route('/api/ocr/translate', methods=['POST'])
@jwt_required()
def ocr_translate():
    try:
        user_id = int(get_jwt_identity())

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
        user_id = int(get_jwt_identity())
        attempts = UserAttempt.query.filter_by(user_id=user_id).order_by(UserAttempt.created_at.desc()).all()

        attempts_data = []
        for attempt in attempts:
            # Get the related learning question
            question = attempt.learning_question
            attempts_data.append({
                'id': attempt.id,
                'learning_question_id': attempt.learning_question_id,
                'question_prompt': question.prompt if question else 'Question not found',
                'question_skill_type': question.skill_type if question else 'unknown',
                'question_level': question.level if question else 0,
                'user_input': attempt.user_input,
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
        user_id = int(get_jwt_identity())
        sessions = TestSession.query.filter_by(user_id=user_id).order_by(TestSession.started_at.desc()).all()

        sessions_data = []
        for session in sessions:
            # Get related test answers
            test_answers = TestAnswer.query.filter_by(test_session_id=session.id).all()
            
            test_answers_data = []
            for answer in test_answers:
                test_answers_data.append({
                    'id': answer.id,
                    'section': answer.section,
                    'task_type': answer.task_type,
                    'score': answer.score,
                    'question_ids': json.loads(answer.combined_question_ids) if answer.combined_question_ids else [],
                    'user_inputs': json.loads(answer.user_inputs) if answer.user_inputs else [],
                    'feedback': json.loads(answer.ai_feedback) if answer.ai_feedback else {},
                    'created_at': answer.created_at.isoformat()
                })
            
            sessions_data.append({
                'id': session.id,
                'total_score': session.total_score,
                'started_at': session.started_at.isoformat(),
                'finished_at': session.finished_at.isoformat() if session.finished_at else None,
                'feedback': json.loads(session.ai_feedback) if session.ai_feedback else {},
                'test_answers': test_answers_data
            })

        return jsonify({'test_sessions': sessions_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/ocr-history', methods=['GET'])
@jwt_required()
def get_user_ocr_history():
    try:
        user_id = int(get_jwt_identity())
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

# Question Management Routes
@app.route('/api/questions/learning', methods=['GET'])
@jwt_required()
def get_all_learning_questions():
    """Get all learning questions with optional filtering"""
    try:
        level = request.args.get('level', type=int)
        skill_type = request.args.get('skill_type')
        
        questions = get_learning_questions_by_level(level, skill_type)
        
        questions_data = []
        for q in questions:
            questions_data.append({
                'id': q.id,
                'skill_type': q.skill_type,
                'level': q.level,
                'prompt': q.prompt,
                'reference_answer': q.reference_answer,
                'keywords': json.loads(q.keywords) if q.keywords else [],
                'created_at': q.created_at.isoformat()
            })
        
        return jsonify({'questions': questions_data}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/questions/test', methods=['GET'])
@jwt_required()
def get_all_test_questions():
    """Get all test questions with optional filtering"""
    try:
        task_type = request.args.get('task_type')
        section = request.args.get('section')
        
        questions = get_test_questions_by_task_type(task_type, section)
        
        questions_data = []
        for q in questions:
            questions_data.append({
                'id': q.id,
                'section': q.section,
                'task_type': q.task_type,
                'prompt': q.prompt,
                'reference_answer': q.reference_answer,
                'keywords': json.loads(q.keywords) if q.keywords else [],
                'created_at': q.created_at.isoformat()
            })
        
        return jsonify({'questions': questions_data}), 200
    
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
