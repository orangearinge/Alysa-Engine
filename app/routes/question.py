import json
from flask import Blueprint, jsonify, request
from app.models.database import db, Lesson, LessonSection, Quiz, QuizQuestion

question_bp = Blueprint('question', __name__)

# This file is now repurposed to handle "Admin/Seeding" for the new Lesson structure
# as requested ("hapus saja ganti yang baru").

@question_bp.route('/api/admin/seed_content', methods=['POST'])
def seed_content():
    """
    Seeds the database with the Mock Data from the frontend requests.
    This is a utility endpoint to quickly populate the backend.
    """
    try:
        # Clear existing data (optional, be careful)
        # LessonSection.query.delete()
        # QuizQuestion.query.delete()
        # Quiz.query.delete()
        # Lesson.query.delete()
        
        # 1. Create Quizzes
        q1 = Quiz(id='q1', title='Speaking Basics Quiz')
        db.session.merge(q1)
        
        q1_questions = [
            QuizQuestion(
                quiz_id='q1',
                question_text='How many parts are there in the Speaking test?',
                options=json.dumps(['1', '2', '3', '4']),
                correct_option_index=2
            ),
            QuizQuestion(
                quiz_id='q1',
                question_text='How long does the Speaking test last?',
                options=json.dumps(['4-5 minutes', '11-14 minutes', '30 minutes', '1 hour']),
                correct_option_index=1
            )
        ]
        for q in q1_questions:
             db.session.add(q) # Merge might be tricky without IDs, so just add. duplicate check omitted for speed.

        # 2. Create Lessons
        
        # SPEAKING
        l1 = Lesson(
            id='1', 
            title='Introduction to IELTS Speaking',
            description='Learn the basics of the Speaking test format.',
            category='Speaking',
            duration_minutes=15
        )
        db.session.merge(l1)
        
        l1_sections = [
            LessonSection(lesson_id='1', title='Overview', content='The IELTS Speaking test consists of 3 parts and lasts 11-14 minutes. It is a face-to-face interview with an examiner.'),
            LessonSection(lesson_id='1', title='Part 1: Introduction and Interview', content='In this part, the examiner asks you general questions about yourself...'),
            LessonSection(lesson_id='1', title='Part 2: Long Turn', content='You will be given a card which asks you to talk about a particular topic...'),
            LessonSection(lesson_id='1', title='Quiz: Speaking Basics', quiz_id='q1')
        ]
        
        l2 = Lesson(id='s2', title='Speaking Part 2 Strategies', description='Master the "Long Turn" with effective note-taking.', category='Speaking', duration_minutes=15)
        db.session.merge(l2)
        l2_sections = [
            LessonSection(lesson_id='s2', title='Using the 1 Minute Preparation', content='Don\'t write full sentences. Write keywords and structure your talk.'),
            LessonSection(lesson_id='s2', title='Structure Your Talk', content='Introduction -> Past -> Present -> Future -> Conclusion/Opinion.')
        ]

        l3 = Lesson(id='s3', title='Common Topics in Speaking Part 1', description='Prepare fo questions about home, work, and hobbies.', category='Speaking', duration_minutes=10)
        db.session.merge(l3)
        l3_sections = [
             LessonSection(lesson_id='s3', title='Home & Hometown', content='Be ready to describe your room, house, or neighborhood.'),
             LessonSection(lesson_id='s3', title='Work & Studies', content='Know the vocabulary for your major or job role.')
        ]

        l4 = Lesson(id='s4', title='Improving Fluency & Coherence', description='Speak naturally without too many pauses.', category='Speaking', duration_minutes=20)
        db.session.merge(l4)
        l4_sections = [
             LessonSection(lesson_id='s4', title='Fillers', content='Use natural fillers like "Well...", "Actually...", "To be honest..." instead of "Umm".')
        ]


        # WRITING
        w1 = Lesson(id='2', title='Writing Task 1: Charts', description='How to describe bar charts effectively.', category='Writing', duration_minutes=25)
        db.session.merge(w1)
        w1_sections = [
             LessonSection(lesson_id='2', title='Understanding Bar Charts', content='Bar charts show comparison between categories.'),
             LessonSection(lesson_id='2', title='Key Vocabulary', content='Use words like "increase", "decrease", "fluctuate".'),
             LessonSection(lesson_id='2', title='Quiz: Bar Charts', quiz_id='q1') # Reusing q1
        ]
        
        w2 = Lesson(id='w2', title='Writing Task 2: Essay Structures', description='Organize your opinion or argument essays clearly.', category='Writing', duration_minutes=30)
        db.session.merge(w2)
        w2_sections = [
            LessonSection(lesson_id='w2', title='4-Paragraph Structure', content='Intro, Body 1, Body 2, Conclusion.'),
            LessonSection(lesson_id='w2', title='Thesis Statement', content='Clearly state your position in the introduction.')
        ]

        w3 = Lesson(id='w3', title='Letter Writing (General Training)', description='Formal vs Informal letters.', category='Writing', duration_minutes=20)
        db.session.merge(w3)
        w3_sections = [
            LessonSection(lesson_id='w3', title='Formal Openings', content='"Dear Sir/Madam,"'),
            LessonSection(lesson_id='w3', title='Informal Openings', content='"Hi John,"')
        ]

        w4 = Lesson(id='w4', title='Vocabulary for Writing', description='Academic words to boost your score.', category='Writing', duration_minutes=15)
        db.session.merge(w4)
        w4_sections = [
            LessonSection(lesson_id='w4', title='Linking Words', content='Furthermore, However, Consequently.')
        ]

        # LISTENING
        li1 = Lesson(id='3', title='Listening for Details', description='Techniques to catch specific information.', category='Listening', duration_minutes=20)
        db.session.merge(li1)
        li1_sections = [
            LessonSection(lesson_id='3', title='Names and Numbers', content='Practice listening for spelling of names and long numbers.')
        ]

        li2 = Lesson(id='l2', title='Predicting Answers', description='Use context to guess the type of word needed.', category='Listening', duration_minutes=20)
        db.session.merge(li2)
        li2_sections = [
             LessonSection(lesson_id='l2', title='Grammar Clues', content='If there is "a" or "an" before the blank, you know it is a singular noun.')
        ]

        li3 = Lesson(id='l3', title='Listening to Accents', description='Familiarize yourself with British, Australian, and American accents.', category='Listening', duration_minutes=15)
        db.session.merge(li3)
        li3_sections = [
            LessonSection(lesson_id='l3', title='The "R" Sound', content='American English emphasizes the "r".')
        ]

        li4 = Lesson(id='l4', title='Map Labeling', description='Navigating directions in Listening Section 2.', category='Listening', duration_minutes=25)
        db.session.merge(li4)
        li4_sections = [
            LessonSection(lesson_id='l4', title='Directional Language', content='North, South, East, West, across from, next to.')
        ]

        # READING
        r1 = Lesson(id='4', title='Reading Skimming Techniques', description='Read faster and find answers quicker.', category='Reading', duration_minutes=30)
        db.session.merge(r1)
        r1_sections = [
            LessonSection(lesson_id='4', title='Read First and Last Sentences', content='Topic sentences often contain the main idea.')
        ]

        r2 = Lesson(id='r2', title='Scanning for Keywords', description='Locate information without reading every word.', category='Reading', duration_minutes=15)
        db.session.merge(r2)
        r2_sections = [
            LessonSection(lesson_id='r2', title='Proper Nouns and Dates', content='Scan for capital letters and numbers.')
        ]
        
        r3 = Lesson(id='r3', title='True, False, Not Given', description='Strategies to handle this tricky question type.', category='Reading', duration_minutes=25)
        db.session.merge(r3)
        r3_sections = [
            LessonSection(lesson_id='r3', title='Not Given vs False', content='False means the text says the opposite. Not Given means missing info.')
        ]

        r4 = Lesson(id='r4', title='Matching Headings', description='Match the correct heading to paragraphs.', category='Reading', duration_minutes=20)
        db.session.merge(r4)
        r4_sections = [
             LessonSection(lesson_id='r4', title='Don\'t rely on flexible keywords', content='Focus on the main idea.')
        ]

        
        # Add all sections
        all_sections = l1_sections + l2_sections + l3_sections + l4_sections + \
                       w1_sections + w2_sections + w3_sections + w4_sections + \
                       li1_sections + li2_sections + li3_sections + li4_sections + \
                       r1_sections + r2_sections + r3_sections + r4_sections
                       
        for s in all_sections:
            db.session.add(s)

        db.session.commit()
        return jsonify({'message': 'Database seeded with mock content successfully!'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
