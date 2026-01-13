from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.database import db, User, OCRTranslation, TestAnswer, TestSession, UserAttempt

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({
            'username': user.username,
            'email': user.email,
            'target_score': user.target_score,
            'daily_study_time_minutes': user.daily_study_time_minutes,
            'test_date': user.test_date.isoformat() if user.test_date else None
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/api/user/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        data = request.get_json()
        
        if 'username' in data and data['username'] is not None:
            # Optional: check if username is already taken
            existing_user = User.query.filter(User.username == data['username'], User.id != user_id).first()
            if existing_user:
                return jsonify({'error': 'Username already taken'}), 400
            user.username = data['username']
            
        if 'email' in data and data['email'] is not None:
            # Optional: check if email is already taken
            existing_email = User.query.filter(User.email == data['email'], User.id != user_id).first()
            if existing_email:
                return jsonify({'error': 'Email already taken'}), 400
            user.email = data['email']

        if 'target_score' in data:
            user.target_score = float(data['target_score'])
        if 'daily_study_time_minutes' in data:
            user.daily_study_time_minutes = int(data['daily_study_time_minutes'])
        if 'test_date' in data:
            try:
                # Handle ISO format string
                user.test_date = datetime.fromisoformat(data['test_date'].replace('Z', '+00:00'))
            except ValueError:
                pass
                
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'username': user.username,
                'email': user.email,
                'target_score': user.target_score,
                'daily_study_time_minutes': user.daily_study_time_minutes,
                'test_date': user.test_date.isoformat() if user.test_date else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/api/user/attempts', methods=['GET'])
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

@user_bp.route('/api/user/test-sessions', methods=['GET'])
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

@user_bp.route('/api/user/ocr-history', methods=['GET'])
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
