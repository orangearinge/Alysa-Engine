import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.utils.helpers import get_learning_questions_by_level, get_test_questions_by_task_type

question_bp = Blueprint('question', __name__)

@question_bp.route('/api/questions/learning', methods=['GET'])
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

@question_bp.route('/api/questions/test', methods=['GET'])
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
