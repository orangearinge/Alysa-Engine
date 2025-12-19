from app import create_app, db
from sqlalchemy import text

app = create_app()

def update_schema():
    with app.app_context():
        with db.engine.connect() as conn:
            print("Updating users table schema...")
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN target_score FLOAT DEFAULT 6.5"))
                print("Added target_score")
            except Exception as e:
                print(f"target_score might already exist: {e}")

            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN daily_study_time_minutes INTEGER DEFAULT 30"))
                print("Added daily_study_time_minutes")
            except Exception as e:
                print(f"daily_study_time_minutes might already exist: {e}")

            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN test_date DATETIME"))
                print("Added test_date")
            except Exception as e:
                print(f"test_date might already exist: {e}")
            
            conn.commit()
            print("Schema update finished.")

if __name__ == "__main__":
    update_schema()
