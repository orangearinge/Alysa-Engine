import json

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from PIL import Image

from app.ai_models.ocr import process_image
from app.models.database import OCRTranslation, db

ocr_bp = Blueprint('ocr', __name__)

@ocr_bp.route('/api/ocr/translate', methods=['POST'])
# @jwt_required()
def ocr_translate():
    try:
        # Get user_id if authenticated, otherwise None
        try:
            user_id = int(get_jwt_identity()) if get_jwt_identity() else None
        except:
            user_id = None

        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400

        # Process image
        image = Image.open(file.stream)
        result = process_image(image)

        if 'error' in result:
            return jsonify({'error': result['error']}), 400

        # Save OCR result to database only if user is authenticated
        record_id = None
        if user_id:
            ocr_record = OCRTranslation(
                user_id=user_id,
                original_text=result.get('detected_language', '') + ': ' + str(result),
                translated_and_explained=json.dumps(result)
            )
            db.session.add(ocr_record)
            db.session.commit()
            record_id = ocr_record.id

        return jsonify({
            'message': 'OCR translation completed',
            'result': result,
            'record_id': record_id
        }), 200


    except Exception as e:
        return jsonify({'error': str(e)}), 500
