import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models.database import Lesson, LessonSection, Quiz, QuizQuestion, UserLessonProgress, db

learning_bp = Blueprint('learning', __name__)

@learning_bp.route('/api/lessons', methods=['GET'])
# @jwt_required() - Optional: make public or protected
def get_lessons():
    """Get all lessons, optionally filtered by category"""
    try:
        category = request.args.get('category')
        
        query = Lesson.query
        if category:
            # Case insensitive filtering
            query = query.filter(Lesson.category.ilike(category))
            
        lessons = query.all()
        
        lessons_data = []
        for lesson in lessons:
            lessons_data.append({
                'id': lesson.id,
                'title': lesson.title,
                'description': lesson.description,
                'category': lesson.category,
                'durationMinutes': lesson.duration_minutes,
                # In real app, check UserLessonProgress here
                'isCompleted': False 
            })
            
        return jsonify({'lessons': lessons_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/api/lessons/<lesson_id>', methods=['GET'])
def get_lesson_detail(lesson_id):
    """Get full lesson details including sections"""
    try:
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return jsonify({'error': 'Lesson not found'}), 404
            
        sections_data = []
        for section in lesson.sections:
            sections_data.append({
                'title': section.title,
                'content': section.content,
                'quizId': section.quiz_id
            })
            
        lesson_data = {
            'id': lesson.id,
            'title': lesson.title,
            'description': lesson.description,
            'category': lesson.category,
            'durationMinutes': lesson.duration_minutes,
            'sections': sections_data
        }
        
        return jsonify(lesson_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/api/quizzes/<quiz_id>', methods=['GET'])
def get_quiz(quiz_id):
    """Get quiz details and questions"""
    try:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
            
        questions_data = []
        for q in quiz.questions:
            questions_data.append({
                'questionText': q.question_text,
                'options': json.loads(q.options) if q.options else [],
                'correctOptionIndex': q.correct_option_index
            })
            
        quiz_data = {
            'id': quiz.id,
            'title': quiz.title,
            'questions': questions_data
        }
        
        return jsonify(quiz_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/api/learning/progress', methods=['POST'])
@jwt_required()
def update_progress():
    """Update lesson completion status"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        lesson_id = data.get('lesson_id')
        is_completed = data.get('is_completed', True)
        
        if not lesson_id:
            return jsonify({'error': 'Missing lesson_id'}), 400
            
        progress = UserLessonProgress.query.filter_by(
            user_id=user_id, lesson_id=lesson_id
        ).first()
        
        if progress:
            progress.is_completed = is_completed
            progress.last_accessed_at = db.func.now()
        else:
            progress = UserLessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                is_completed=is_completed
            )
            db.session.add(progress)
            
        db.session.commit()
        
        return jsonify({'message': 'Progress updated'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
