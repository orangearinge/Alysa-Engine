from app import create_app
from app.models.database import db

# Create app instance
app = create_app()

if __name__ == '__main__':
    # Initialize database tables
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
