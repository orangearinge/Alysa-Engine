import json
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.database import db, TestQuestion, TestSession, TestAnswer

test_bp = Blueprint('test', __name__)

@test_bp.route('/api/test/start', methods=['POST'])
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

@test_bp.route('/api/test/submit', methods=['POST'])
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

        # Import AI feedback function here to avoid circular imports
        from app.ai_models.gemini import ai_toefl_feedback as gemini_feedback

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
