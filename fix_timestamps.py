import os
import sys
from datetime import datetime, timedelta

# Add parent directory to sys.path to import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app import create_app
from app.models.database import db, User, Lesson, UserLessonProgress, TestQuestion, UserAttempt, TestSession, TestAnswer, OCRTranslation

app = create_app()

def fix_all_timestamps():
    with app.app_context():
        print("Starting timestamp correction (adding 7 hours)...")
        
        # List of models and their timestamp columns
        corrections = [
            (User, ['created_at']),
            (Lesson, ['created_at']),
            (UserLessonProgress, ['last_accessed_at']),
            (TestQuestion, ['created_at']),
            (UserAttempt, ['created_at']),
            (TestSession, ['started_at', 'finished_at']),
            (TestAnswer, ['created_at']),
            (OCRTranslation, ['created_at'])
        ]
        
        for Model, columns in corrections:
            print(f"Processing {Model.__tablename__}...")
            records = Model.query.all()
            count = 0
            for record in records:
                updated = False
                for col in columns:
                    val = getattr(record, col)
                    if val:
                        # Add 7 hours to convert from UTC to WIB
                        setattr(record, col, val + timedelta(hours=7))
                        updated = True
                if updated:
                    count += 1
            
            print(f"Updated {count} records in {Model.__tablename__}.")
        
        db.session.commit()
        print("All timestamps corrected successfully!")

if __name__ == "__main__":
    fix_all_timestamps()
