from flask import Blueprint, request, jsonify
from gradio_client import Client
from flask_jwt_extended import jwt_required

chatbot_bp = Blueprint('chatbot', __name__)

# Initialize connection immediately or lazily? 
# Usually better to do it lazily or at module level if it's safe.
# The user's snippet initializes it directly. 
# We'll put it in a try-catch block or initialize it globally.
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
        # The user provided snippet:
        # result = client.predict(
        # 	question="Hello!!",
        # 	api_name="/alysa_rag_chatbot"
        # )
        result = client.predict(
            question=user_message,
            api_name="/alysa_rag_chatbot"
        )
        
        # result is likely the response string or tuple depending on the gradio app return type.
        # Based on typical rag-chatbot, it's usually a string or a tuple (answer, history).
        # We will return the result as is or wrap it.
        # Assuming result is the string response for now based on user snippet 'print(result)'.
        
        return jsonify({'response': result})

    except Exception as e:
        print(f"Error calling chatbot: {e}")
        return jsonify({'error': str(e)}), 500
