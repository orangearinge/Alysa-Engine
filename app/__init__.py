from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Import models and initialize database
from app.models.database import db

# Import blueprints
from app.routes.auth import auth_bp
from app.routes.learning import learning_bp
from app.routes.ocr import ocr_bp
from app.routes.question import question_bp
from app.routes.test import test_bp
from app.routes.user import user_bp
from app.routes.admin import admin_bp
from config import Config

# Import Firebase initialization
from app.firebase_config import initialize_firebase

# Load environment variables
load_dotenv()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)

    # Configuration
    app.config.from_object(Config)

    # Initialize Firebase Admin SDK
    initialize_firebase()

    # Initialize extensions
    db.init_app(app)
    JWTManager(app)
    CORS(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(learning_bp)
    app.register_blueprint(test_bp)
    app.register_blueprint(ocr_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(question_bp)
    app.register_blueprint(admin_bp)

    # Health check route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        from flask import jsonify
        return jsonify({'status': 'healthy', 'message': 'TOEFL Learning API is running'}), 200

    @app.route('/', methods=['GET'])
    def home():
        from flask import jsonify
        return jsonify({'status': 'healthy', 'message': 'TOEFL Learning API is running'}), 200

    return app
