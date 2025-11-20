import json

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models.database import OCRTranslation, TestAnswer, TestSession, UserAttempt

user_bp = Blueprint('user', __name__)

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
