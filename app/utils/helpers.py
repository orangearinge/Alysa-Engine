import bcrypt

from app.models.database import LearningQuestion, TestQuestion


# Helper functions for password management
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

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
