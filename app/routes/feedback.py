from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.database import db, UserFeedback, User
from app.utils.sentiment_analyzer import analyze_sentiment
from datetime import datetime

feedback_bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')

@feedback_bp.route('', methods=['POST'])
@jwt_required()
def submit_feedback():
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    data = request.get_json()
    
    if not data or 'feedback_text' not in data:
        return jsonify({'error': 'Feedback text is required'}), 400
    
    feedback_text = data['feedback_text']
    
    # Perform sentiment analysis
    sentiment = analyze_sentiment(feedback_text)
    
    try:
        new_feedback = UserFeedback(
            user_id=current_user.id,
            feedback_text=feedback_text,
            sentiment=sentiment,
            created_at=datetime.now()
        )
        db.session.add(new_feedback)
        db.session.commit()
        
        return jsonify({
            'message': 'Feedback submitted successfully',
            'sentiment': sentiment
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
