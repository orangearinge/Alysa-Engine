import json

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models.database import LearningQuestion, UserAttempt, db
from app.utils.helpers import get_learning_questions_by_level

learning_bp = Blueprint('learning', __name__)

@learning_bp.route('/api/learning/questions', methods=['GET'])
@jwt_required()
def get_learning_questions():
    try:
        # Get query parameters
        level = request.args.get('level', type=int)
        skill_type = request.args   .get('skill_type')

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

@learning_bp.route('/api/learning/submit', methods=['POST'])
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

        # Import AI feedback functions here to avoid circular imports
        from app.ai_models.alysa import ai_toefl_feedback as alysa_feedback
        from app.ai_models.gemini import ai_toefl_feedback as gemini_feedback

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
