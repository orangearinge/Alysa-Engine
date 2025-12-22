from firebase_admin import auth as firebase_auth
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from app.models.database import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/firebase-login', methods=['POST'])
def firebase_login():
    """
    Endpoint for logging in with Firebase ID Token.
    Verifies the token, creates/retrieves user, and issues a JWT access token.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid Authorization header'}), 401

    id_token = auth_header.split('Bearer ')[1].strip()

    # Debug: Print incoming token details
    print(f"Received ID Token (len={len(id_token)}): {id_token[:10]}...")

    try:
        # Verify Firebase Token
        decoded_token = firebase_auth.verify_id_token(id_token)
        email = decoded_token.get('email')

        if not email:
            return jsonify({'error': 'Email is required from Firebase provider'}), 400

        # Check if user exists in DB
        user = User.query.filter_by(email=email).first()

        if not user:
            # Create new user
            # Generate a username from email
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            # Ensure username is unique
            while User.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1

            new_user = User(
                username=username,
                email=email
            )

            db.session.add(new_user)
            db.session.commit()
            user = new_user

        # Create access token (JWT)
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200

    except ValueError as e:
        print(f"Firebase Token Verification Failed: {e}")
        return jsonify({'error': f'Invalid token format or signature: {str(e)}'}), 401
    except Exception as e:
        print(f"Firebase login error: {e}")
        return jsonify({'error': f'Authentication failed: {str(e)}'}), 401
