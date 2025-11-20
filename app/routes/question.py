import json
from functools import wraps

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_jwt_extended import jwt_required

from app.models.database import LearningQuestion, TestQuestion, db
from app.utils.helpers import (
    get_learning_questions_by_level,
    get_test_questions_by_task_type,
)

question_bp = Blueprint('question', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('question.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Admin Routes ---

@question_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == current_app.config.get('ADMIN_USERNAME') and password == current_app.config.get('ADMIN_PASSWORD'):
            session['admin_logged_in'] = True
            return redirect(url_for('question.admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')

    return render_template('admin/login.html')

@question_bp.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('question.admin_login'))

@question_bp.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

# --- Learning Question CRUD ---

@question_bp.route('/admin/learning')
@admin_required
def admin_learning_list():
    questions = LearningQuestion.query.order_by(LearningQuestion.created_at.desc()).all()
    return render_template('admin/learning_list.html', questions=questions)

@question_bp.route('/admin/learning/new', methods=['GET', 'POST'])
@admin_required
def admin_learning_create():
    if request.method == 'POST':
        try:
            question = LearningQuestion(
                skill_type=request.form['skill_type'],
                level=int(request.form['level']),
                prompt=request.form['prompt'],
                reference_answer=request.form.get('reference_answer'),
                keywords=request.form.get('keywords', '[]')
            )
            db.session.add(question)
            db.session.commit()
            flash('Question created successfully', 'success')
            return redirect(url_for('question.admin_learning_list'))
        except Exception as e:
            flash(f'Error creating question: {str(e)}', 'error')

    return render_template('admin/learning_form.html', question=None)

@question_bp.route('/admin/learning/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_learning_edit(id):
    question = LearningQuestion.query.get_or_404(id)

    if request.method == 'POST':
        try:
            question.skill_type = request.form['skill_type']
            question.level = int(request.form['level'])
            question.prompt = request.form['prompt']
            question.reference_answer = request.form.get('reference_answer')
            question.keywords = request.form.get('keywords', '[]')

            db.session.commit()
            flash('Question updated successfully', 'success')
            return redirect(url_for('question.admin_learning_list'))
        except Exception as e:
            flash(f'Error updating question: {str(e)}', 'error')

    return render_template('admin/learning_form.html', question=question)

@question_bp.route('/admin/learning/delete/<int:id>', methods=['POST'])
@admin_required
def admin_learning_delete(id):
    question = LearningQuestion.query.get_or_404(id)
    try:
        db.session.delete(question)
        db.session.commit()
        flash('Question deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting question: {str(e)}', 'error')
    return redirect(url_for('question.admin_learning_list'))

# --- Test Question CRUD ---

@question_bp.route('/admin/test')
@admin_required
def admin_test_list():
    questions = TestQuestion.query.order_by(TestQuestion.created_at.desc()).all()
    return render_template('admin/test_list.html', questions=questions)

@question_bp.route('/admin/test/new', methods=['GET', 'POST'])
@admin_required
def admin_test_create():
    if request.method == 'POST':
        try:
            question = TestQuestion(
                section=request.form['section'],
                task_type=request.form['task_type'],
                prompt=request.form['prompt'],
                reference_answer=request.form.get('reference_answer'),
                keywords=request.form.get('keywords', '[]')
            )
            db.session.add(question)
            db.session.commit()
            flash('Question created successfully', 'success')
            return redirect(url_for('question.admin_test_list'))
        except Exception as e:
            flash(f'Error creating question: {str(e)}', 'error')

    return render_template('admin/test_form.html', question=None)

@question_bp.route('/admin/test/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_test_edit(id):
    question = TestQuestion.query.get_or_404(id)

    if request.method == 'POST':
        try:
            question.section = request.form['section']
            question.task_type = request.form['task_type']
            question.prompt = request.form['prompt']
            question.reference_answer = request.form.get('reference_answer')
            question.keywords = request.form.get('keywords', '[]')

            db.session.commit()
            flash('Question updated successfully', 'success')
            return redirect(url_for('question.admin_test_list'))
        except Exception as e:
            flash(f'Error updating question: {str(e)}', 'error')

    return render_template('admin/test_form.html', question=question)

@question_bp.route('/admin/test/delete/<int:id>', methods=['POST'])
@admin_required
def admin_test_delete(id):
    question = TestQuestion.query.get_or_404(id)
    try:
        db.session.delete(question)
        db.session.commit()
        flash('Question deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting question: {str(e)}', 'error')
    return redirect(url_for('question.admin_test_list'))

# --- API Routes ---

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
