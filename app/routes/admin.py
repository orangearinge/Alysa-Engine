from datetime import datetime
from sqlalchemy import or_
from app.models.database import db, User, Lesson, LessonSection, Quiz, QuizQuestion, TestQuestion, TestSession, UserAttempt
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# Dashboard & Auth
# ==========================================

@admin_bp.route('/')
@login_required
def dashboard():
    stats = {
        'users': User.query.count(),
        'lessons': Lesson.query.count(),
        'quizzes': Quiz.query.count(),
        'tests': TestQuestion.query.count(),
        'sessions': TestSession.query.count(),
        'attempts': UserAttempt.query.count(),
    }
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_sessions = TestSession.query.order_by(TestSession.started_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_users=recent_users, 
                         recent_sessions=recent_sessions)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin_username = os.environ.get('ADMIN_USERNAME')
        admin_password = os.environ.get('ADMIN_PASSWORD')

        if not admin_username or not admin_password:
             flash('Admin credentials not configured in environment', 'error')
             return render_template('admin/login.html')

        if username == admin_username and password == admin_password:
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials', 'error')
            
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))

# ==========================================
# User Management
# ==========================================

@admin_bp.route('/users')
@login_required
def users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    
    query = User.query
    if search:
        query = query.filter(or_(User.username.ilike(f'%{search}%'), User.email.ilike(f'%{search}%')))
    
    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/users.html', pagination=pagination, search=search)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'error')
    return redirect(url_for('admin.users'))

# ==========================================
# Learning Management
# ==========================================

@admin_bp.route('/learning')
@login_required
def learning():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    
    query = Lesson.query
    if search:
        query = query.filter(or_(Lesson.title.ilike(f'%{search}%'), Lesson.description.ilike(f'%{search}%')))
    if category:
        query = query.filter(Lesson.category == category)
        
    categories = db.session.query(Lesson.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]

    pagination = query.order_by(Lesson.id).paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/learning.html', pagination=pagination, search=search, category=category, categories=categories)

@admin_bp.route('/learning/create', methods=['GET', 'POST'])
@login_required
def create_lesson():
    if request.method == 'POST':
        lesson_id = request.form.get('id')
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        duration = request.form.get('duration')
        
        existing = Lesson.query.get(lesson_id)
        if existing:
            flash(f'Lesson with ID {lesson_id} already exists', 'error')
        else:
            try:
                new_lesson = Lesson(
                    id=lesson_id,
                    title=title,
                    description=description,
                    category=category,
                    duration_minutes=int(duration) if duration else 0
                )
                db.session.add(new_lesson)
                db.session.commit()
                flash('Lesson created successfully', 'success')
                return redirect(url_for('admin.learning'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating lesson: {str(e)}', 'error')

    return render_template('admin/learning_form.html')

@admin_bp.route('/learning/edit/<lesson_id>', methods=['GET', 'POST'])
@login_required
def edit_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    if request.method == 'POST':
        lesson.title = request.form.get('title')
        lesson.description = request.form.get('description')
        lesson.category = request.form.get('category')
        duration = request.form.get('duration')
        lesson.duration_minutes = int(duration) if duration else 0
        
        try:
            db.session.commit()
            flash('Lesson updated successfully', 'success')
            return redirect(url_for('admin.learning'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating lesson: {str(e)}', 'error')

    return render_template('admin/learning_form.html', lesson=lesson)

@admin_bp.route('/learning/delete/<lesson_id>', methods=['POST'])
@login_required
def delete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    try:
        db.session.delete(lesson)
        db.session.commit()
        flash('Lesson deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting lesson: {str(e)}', 'error')
    return redirect(url_for('admin.learning'))

@admin_bp.route('/learning/<lesson_id>/sections')
@login_required
def learning_sections(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    return render_template('admin/learning_sections.html', lesson=lesson)

@admin_bp.route('/learning/<lesson_id>/sections/create', methods=['POST'])
@login_required
def create_section(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    title = request.form.get('title')
    content = request.form.get('content')
    quiz_id = request.form.get('quiz_id')
    
    try:
        new_section = LessonSection(
            lesson_id=lesson.id,
            title=title,
            content=content,
            quiz_id=quiz_id if quiz_id else None
        )
        db.session.add(new_section)
        db.session.commit()
        flash('Section created successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating section: {str(e)}', 'error')
        
    return redirect(url_for('admin.learning_sections', lesson_id=lesson_id))

@admin_bp.route('/learning/sections/edit/<int:section_id>', methods=['POST'])
@login_required
def edit_section(section_id):
    section = LessonSection.query.get_or_404(section_id)
    section.title = request.form.get('title')
    section.content = request.form.get('content')
    quiz_id = request.form.get('quiz_id')
    section.quiz_id = quiz_id if quiz_id else None
    
    try:
        db.session.commit()
        flash('Section updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating section: {str(e)}', 'error')
        
    return redirect(url_for('admin.learning_sections', lesson_id=section.lesson_id))

@admin_bp.route('/learning/sections/delete/<int:section_id>', methods=['POST'])
@login_required
def delete_section(section_id):
    section = LessonSection.query.get_or_404(section_id)
    lesson_id = section.lesson_id
    try:
        db.session.delete(section)
        db.session.commit()
        flash('Section deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting section: {str(e)}', 'error')
    return redirect(url_for('admin.learning_sections', lesson_id=lesson_id))

# ==========================================
# Quiz Management
# ==========================================

@admin_bp.route('/quiz')
@login_required
def quiz():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    
    query = Quiz.query
    if search:
        query = query.filter(Quiz.title.ilike(f'%{search}%'))
        
    pagination = query.order_by(Quiz.id).paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/quiz.html', pagination=pagination, search=search)

@admin_bp.route('/quiz/create', methods=['GET', 'POST'])
@login_required
def create_quiz():
    if request.method == 'POST':
        quiz_id = request.form.get('id')
        title = request.form.get('title')
        
        existing = Quiz.query.get(quiz_id)
        if existing:
            flash(f'Quiz with ID {quiz_id} already exists', 'error')
        else:
            try:
                new_quiz = Quiz(id=quiz_id, title=title)
                db.session.add(new_quiz)
                db.session.commit()
                flash('Quiz created successfully', 'success')
                return redirect(url_for('admin.quiz'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating quiz: {str(e)}', 'error')

    return render_template('admin/quiz_form.html')

@admin_bp.route('/quiz/edit/<quiz_id>', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        quiz.title = request.form.get('title')
        try:
            db.session.commit()
            flash('Quiz updated successfully', 'success')
            return redirect(url_for('admin.quiz'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating quiz: {str(e)}', 'error')

    return render_template('admin/quiz_form.html', quiz=quiz)

@admin_bp.route('/quiz/delete/<quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    try:
        db.session.delete(quiz)
        db.session.commit()
        flash('Quiz deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting quiz: {str(e)}', 'error')
    return redirect(url_for('admin.quiz'))

@admin_bp.route('/quiz/<quiz_id>/questions')
@login_required
def quiz_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    import json
    for q in quiz.questions:
         try:
             q.parsed_options = json.loads(q.options) if q.options else []
         except:
             q.parsed_options = []
    return render_template('admin/quiz_questions.html', quiz=quiz)

@admin_bp.route('/quiz/<quiz_id>/questions/create', methods=['POST'])
@login_required
def create_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    question_text = request.form.get('question_text')
    options_list = [
        request.form.get('option_0'),
        request.form.get('option_1'),
        request.form.get('option_2'),
        request.form.get('option_3')
    ]
    correct_option_index = request.form.get('correct_option_index')
    import json
    try:
        new_question = QuizQuestion(
            quiz_id=quiz.id,
            question_text=question_text,
            options=json.dumps(options_list),
            correct_option_index=int(correct_option_index) if correct_option_index is not None else 0
        )
        db.session.add(new_question)
        db.session.commit()
        flash('Question added successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding question: {str(e)}', 'error')
    return redirect(url_for('admin.quiz_questions', quiz_id=quiz_id))

@admin_bp.route('/quiz/questions/edit/<int:question_id>', methods=['POST'])
@login_required
def edit_question(question_id):
    question = QuizQuestion.query.get_or_404(question_id)
    question.question_text = request.form.get('question_text')
    options_list = [
        request.form.get('option_0'),
        request.form.get('option_1'),
        request.form.get('option_2'),
        request.form.get('option_3')
    ]
    correct_option_index = request.form.get('correct_option_index')
    import json
    question.options = json.dumps(options_list)
    question.correct_option_index = int(correct_option_index) if correct_option_index is not None else 0
    try:
        db.session.commit()
        flash('Question updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating question: {str(e)}', 'error')
    return redirect(url_for('admin.quiz_questions', quiz_id=question.quiz_id))

@admin_bp.route('/quiz/questions/delete/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    question = QuizQuestion.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    try:
        db.session.delete(question)
        db.session.commit()
        flash('Question deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting question: {str(e)}', 'error')
    return redirect(url_for('admin.quiz_questions', quiz_id=quiz_id))

# ==========================================
# Test Management
# ==========================================

@admin_bp.route('/tests')
@login_required
def tests():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    section = request.args.get('section', '').strip()
    task_type = request.args.get('task_type', '').strip()
    
    query = TestQuestion.query
    if search:
        query = query.filter(TestQuestion.prompt.ilike(f'%{search}%'))
    if section:
        query = query.filter(TestQuestion.section == section)
    if task_type:
        query = query.filter(TestQuestion.task_type == task_type)
        
    pagination = query.order_by(TestQuestion.id).paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/tests.html', pagination=pagination, search=search, section=section, task_type=task_type)

@admin_bp.route('/tests/create', methods=['GET', 'POST'])
@login_required
def create_test_question():
    if request.method == 'POST':
        section = request.form.get('section')
        task_type = request.form.get('task_type')
        prompt = request.form.get('prompt')
        reference_answer = request.form.get('reference_answer')
        keywords_str = request.form.get('keywords', '')
        keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
        import json
        try:
            new_q = TestQuestion(
                section=section,
                task_type=task_type,
                prompt=prompt,
                reference_answer=reference_answer,
                keywords=json.dumps(keywords)
            )
            db.session.add(new_q)
            db.session.commit()
            flash('Test question created successfully', 'success')
            return redirect(url_for('admin.tests'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating test question: {str(e)}', 'error')
    return render_template('admin/test_form.html')

@admin_bp.route('/tests/edit/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_test_question(question_id):
    question = TestQuestion.query.get_or_404(question_id)
    import json
    if request.method == 'POST':
        question.section = request.form.get('section')
        question.task_type = request.form.get('task_type')
        question.prompt = request.form.get('prompt')
        question.reference_answer = request.form.get('reference_answer')
        keywords_str = request.form.get('keywords', '')
        keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
        question.keywords = json.dumps(keywords)
        try:
            db.session.commit()
            flash('Test question updated successfully', 'success')
            return redirect(url_for('admin.tests'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating test question: {str(e)}', 'error')
    try:
        keywords_list = json.loads(question.keywords) if question.keywords else []
        current_keywords = ', '.join(keywords_list)
    except:
        current_keywords = ''
    return render_template('admin/test_form.html', question=question, current_keywords=current_keywords)

@admin_bp.route('/tests/delete/<int:question_id>', methods=['POST'])
@login_required
def delete_test_question(question_id):
    question = TestQuestion.query.get_or_404(question_id)
    try:
        db.session.delete(question)
        db.session.commit()
        flash('Test question deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting test question: {str(e)}', 'error')
    return redirect(url_for('admin.tests'))

