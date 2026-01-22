import json

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from PIL import Image

from app.ai_models.ocr import process_image
from app.models.database import OCRTranslation, db

ocr_bp = Blueprint('ocr', __name__)

@ocr_bp.route('/api/ocr/translate', methods=['POST'])
@jwt_required(optional=True)
def ocr_translate():
    try:
        # Get user_id if authenticated, otherwise None
        identity = get_jwt_identity()
        print(f"OCR Request incoming. Identity: {identity}")
        try:
            user_id = int(identity) if identity else None
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


@ocr_bp.route('/api/user/ocr-history', methods=['GET'])
@jwt_required()
def get_ocr_history():
    """
    Get OCR translation history for the authenticated user
    Query params:
    - page: page number (default: 1)
    - per_page: items per page (default: 20, max: 100)
    """
    try:
        user_id = int(get_jwt_identity())

        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)

        # Query OCR translations for this user, ordered by most recent first
        pagination = OCRTranslation.query.filter_by(user_id=user_id)\
            .order_by(OCRTranslation.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)

        # Format the results
        history = []
        for record in pagination.items:
            try:
                # Parse the JSON result
                result_data = json.loads(record.translated_and_explained)

                history.append({
                    'id': record.id,
                    'translation': result_data.get('translation', ''),
                    'sentence_analysis': result_data.get('sentence_analysis', []),
                    'detected_language': result_data.get('detected_language', ''),
                    'created_at': record.created_at.isoformat() if record.created_at else None,
                })
            except json.JSONDecodeError:
                # If JSON parsing fails, skip this record
                continue

        return jsonify({
            'history': history,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total_pages': pagination.pages,
                'total_items': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
