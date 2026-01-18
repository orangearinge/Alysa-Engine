import json
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models.database import TestAnswer, TestQuestion, TestSession, db

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

            # Validate score is within expected range (IELTS 0-9)
            if not isinstance(task_score, (int, float)) or task_score < 0 or task_score > 9:
                task_score = 0  # Default to 0 if invalid score
            
            # Ensure score is rounded to nearest 0.5 for IELTS standard
            task_score = round(float(task_score) * 2) / 2

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
        # IELTS performance level descriptors (Bands 0-9)
        if overall_score >= 8.5:
            performance_level = "Expert User (Band 9)"
        elif overall_score >= 7.5:
            performance_level = "Very Good User (Band 8)"
        elif overall_score >= 6.5:
            performance_level = "Good User (Band 7)"
        elif overall_score >= 5.5:
            performance_level = "Competent User (Band 6)"
        elif overall_score >= 4.5:
            performance_level = "Modest User (Band 5)"
        elif overall_score >= 3.5:
            performance_level = "Limited User (Band 4)"
        elif overall_score >= 2.5:
            performance_level = "Extremely Limited User (Band 3)"
        elif overall_score >= 1.5:
            performance_level = "Intermittent User (Band 2)"
        elif overall_score >= 0.5:
            performance_level = "Non User (Band 1)"
        else:
            performance_level = "Did not attempt (Band 0)"

        # Generate overall feedback
        overall_feedback = f"IELTS Test Evaluation - Overall Score: {overall_score:.1f}/9.0 - Performance Level: {performance_level}"

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
                'test_type': 'IELTS Writing & Speaking'
            },
            'evaluation_summary': {
                'overall_feedback': overall_feedback,
                'detailed_task_feedback': detailed_feedback
            },
            'scoring_criteria': {
                'scale': '0-9 Band Score per task',
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

@test_bp.route('/api/test/practice/start', methods=['POST'])
@jwt_required()
def start_practice_test():
    """
    Start a Practice Test session with 10 random questions (5 Writing, 5 Speaking).
    """
    try:
        user_id = int(get_jwt_identity())
        
        # 1. Fetch random questions
        # We need 5 Speaking and 5 Writing
        speaking_questions = TestQuestion.query.filter(TestQuestion.section.ilike('speaking')).order_by(db.func.random()).limit(5).all()
        writing_questions = TestQuestion.query.filter(TestQuestion.section.ilike('writing')).order_by(db.func.random()).limit(5).all()
        
        # Combine and shuffle
        import random
        all_questions = speaking_questions + writing_questions
        random.shuffle(all_questions)
        
        # Ensure we have enough questions (handling dev env with few questions)
        if not all_questions:
             # Fallback if DB is small: just get what we have
             all_questions = TestQuestion.query.order_by(db.func.random()).limit(10).all()

        # Create new test session (Practice Mode)
        test_session = TestSession(
            user_id=user_id,
            total_score=0.0,
            ai_feedback='Practice Test in progress'
        )
        db.session.add(test_session)
        db.session.commit()

        # Format for response
        questions_data = []
        for i, q in enumerate(all_questions):
            questions_data.append({
                'id': i + 1, # Sequential ID for frontend
                'question_id': q.id, # DB ID
                'section': q.section, # 'Speaking' or 'Writing'
                'prompt': q.prompt,
                'task_type': q.task_type
            })

        return jsonify({
            'message': 'Practice test started',
            'session_id': test_session.id,
            'questions': questions_data
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@test_bp.route('/api/test/practice/submit', methods=['POST'])
@jwt_required()
def submit_practice_test():
    """
    Submit Practice Test answers.
    Submit Practice Test answers.
    Expects list of answers. Evaluates each using Gemini or Alysa model.
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data or not data.get('session_id') or not data.get('answers'):
             return jsonify({'error': 'Missing session_id or answers'}), 400

        session_id = data.get('session_id')
        answers = data.get('answers') # List of {question_id, answer, section}
        model_type = data.get('model', 'gemini').lower() # Default to gemini

        # Find test session
        session = TestSession.query.filter_by(id=session_id, user_id=user_id).first()
        if not session:
            return jsonify({'error': 'Test session not found'}), 404

        # Import AI feedback modules
        from app.ai_models.gemini import ai_toefl_feedback as gemini_feedback
        from app.ai_models.Alysa.examiner import evaluate as alysa_evaluate

        total_score = 0
        evaluated_count = 0
        detailed_feedback_list = []
        
        # Process each answer
        for ans in answers:
            q_id = ans.get('question_id')
            user_text = ans.get('answer', '').strip()
            section = ans.get('section', 'General')
            
            if not user_text:
                detailed_feedback_list.append({
                    'question_id': q_id,
                    'user_answer': '',
                    'score': 0,
                    'feedback': ['No answer provided.']
                })
                continue

            # Evaluate Based on Model Selection
            feedback_result = {}
            score = 0

            if model_type == 'alysa':
                # Alysa Model requires Question Prompt + Answer
                # We need to fetch the question prompt from DB
                question = TestQuestion.query.get(q_id)
                if question:
                     # Use Alysa Model
                     feedback_result = alysa_evaluate(question.prompt, user_text)
                else:
                     feedback_result = {
                         'score': 0,
                         'feedback': ["Error: Question not found for Alysa evaluation."]
                     }
            else:
                # Default: Gemini Model (Test Mode) -> Only needs Answer
                feedback_result = gemini_feedback(user_text, mode="test")
            
            score = feedback_result.get('score', 0)
            # Ensure score is rounded to nearest 0.5 for IELTS standard
            score = round(float(score) * 2) / 2
            
            total_score += score
            evaluated_count += 1
            
            # Save simple record (could be improved with TestAnswer model relation if needed strictly)
            test_answer = TestAnswer(
                test_session_id=session.id,
                section=section,
                task_type=f'Practice ({model_type.upper()})', 
                combined_question_ids=json.dumps([q_id]),
                user_inputs=json.dumps([{'q_id': q_id, 'answer': user_text}]),
                ai_feedback=json.dumps(feedback_result),
                score=score
            )
            db.session.add(test_answer)

            detailed_feedback_list.append({
                'question_id': q_id,
                'user_answer': user_text,
                'score': score,
                'feedback': feedback_result.get('feedback', [])
            })

        # Finalize Session
        # Calculate average band score (0-9)
        avg_band_score = total_score / evaluated_count if evaluated_count > 0 else 0
        # Normalize to 0-10 scale for the 10-question test
        # Formula: (avg_band_score / 9.0) * 10.0
        normalized_score = (avg_band_score / 9.0) * 10.0
        avg_score = round(normalized_score, 1)
        
        session.total_score = avg_score
        session.finished_at = datetime.utcnow()
        session.ai_feedback = json.dumps({'detailed_feedback': detailed_feedback_list})
        
        db.session.commit()

        return jsonify({
            'message': 'Practice test evaluated',
            'overall_score': round(avg_score, 1),
            'results': detailed_feedback_list
        }), 200

    except Exception as e:
        print(f"Error in practice submit: {e}")
        return jsonify({'error': str(e)}), 500

@test_bp.route('/api/test/session/<int:session_id>', methods=['GET'])
@jwt_required()
def get_test_session_details(session_id):
    """
    Get detailed results for a specific test session.
    """
    try:
        user_id = int(get_jwt_identity())
        
        # Verify session belongs to user
        session = TestSession.query.filter_by(id=session_id, user_id=user_id).first()
        if not session:
            return jsonify({'error': 'Test session not found'}), 404

        # Get answers
        test_answers = TestAnswer.query.filter_by(test_session_id=session.id).all()
        
        answers_data = []
        for answer in test_answers:
            try:
                display_q_ids = json.loads(answer.combined_question_ids) if answer.combined_question_ids else []
            except json.JSONDecodeError:
                display_q_ids = []

            try:
                display_inputs = json.loads(answer.user_inputs) if answer.user_inputs else []
            except json.JSONDecodeError:
                display_inputs = []

            try:
                display_feedback = json.loads(answer.ai_feedback) if answer.ai_feedback else {}
            except json.JSONDecodeError:
                display_feedback = {'message': str(answer.ai_feedback)}

            answers_data.append({
                'id': answer.id,
                'section': answer.section,
                'task_type': answer.task_type,
                'score': answer.score,
                'question_ids': display_q_ids,
                'user_inputs': display_inputs,
                'feedback': display_feedback
            })
        
        # Safe load session feedback
        try:
            session_feedback = json.loads(session.ai_feedback) if session.ai_feedback else {}
        except json.JSONDecodeError:
             session_feedback = {'overall_feedback': str(session.ai_feedback)}

        return jsonify({
            'session_id': session.id,
            'total_score': session.total_score,
            'started_at': session.started_at.isoformat() if session.started_at else datetime.now().isoformat(),
            'finished_at': session.finished_at.isoformat() if session.finished_at else None,
            'feedback': session_feedback,
            'test_answers': answers_data
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
