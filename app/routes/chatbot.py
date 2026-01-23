from flask import Blueprint, request, jsonify
from gradio_client import Client
from flask_jwt_extended import jwt_required

chatbot_bp = Blueprint('chatbot', __name__)

try:
    print("Initializing Gradio Client for Chatbot...")
    client = Client("alifiashasa/rag-chatbot-alysa")
    print("Gradio Client Initialized.")
except Exception as e:
    print(f"Failed to initialize Gradio Client: {e}")
    client = None

@chatbot_bp.route('/api/chatbot/chat', methods=['POST'])
@jwt_required()
def chat():
    if not client:
        return jsonify({'error': 'Chatbot service unavailable'}), 503

    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400

    user_message = data['message']

    try:
        result = client.predict(
            message=user_message,
            api_name="/alysa_chat"
        )
        
        return jsonify({'response': result})

    except Exception as e:
        print(f"Error calling chatbot: {e}")
        return jsonify({'error': str(e)}), 500
