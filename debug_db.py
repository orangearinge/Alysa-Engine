from app.models.database import db, LessonSection, Quiz
from app import create_app

app = create_app()

with app.app_context():
    print("--- CHECKING DATABASE CONTENT ---")
    
    sections = LessonSection.query.all()
    print(f"Total Lesson Sections: {len(sections)}")
    
    for section in sections:
        if section.quiz_id:
            print(f"Section '{section.title}' points to Quiz ID: '{section.quiz_id}'")
            quiz = Quiz.query.get(section.quiz_id)
            if quiz:
                print(f"  -> FOUND Quiz: {quiz.title} (ID: {quiz.id})")
                print(f"  -> Questions count: {len(quiz.questions)}")
            else:
                print(f"  -> ERROR: Quiz ID '{section.quiz_id}' NOT FOUND in Quizzes table!")

    quizzes = Quiz.query.all()
    print(f"\nTotal Quizzes in DB: {len(quizzes)}")
    for q in quizzes:
        print(f"  - Quiz ID: {q.id}, Title: {q.title}")

    print("--- END CHECK ---")
