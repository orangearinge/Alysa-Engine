#!/usr/bin/env python3
"""
Database initialization script for TOEFL Learning System
Run this script to create the database and tables
"""

from urllib.parse import urlparse
import pymysql
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config import Config

# Create a minimal Flask app for database initialization
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS

db = SQLAlchemy(app)

# --- Database Models ---

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    attempts = db.relationship('UserAttempt', backref='user', lazy=True)
    test_sessions = db.relationship('TestSession', backref='user', lazy=True)
    ocr_translations = db.relationship('OCRTranslation', backref='user', lazy=True)
    lesson_progress = db.relationship('UserLessonProgress', backref='user', lazy=True)
    
    # User Profile Fields
    target_score = db.Column(db.Float, default=6.5)
    daily_study_time_minutes = db.Column(db.Integer, default=30)
    test_date = db.Column(db.DateTime)

class Lesson(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.String(50), primary_key=True) 
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50)) # Speaking, Writing, Reading, Listening
    duration_minutes = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sections = db.relationship('LessonSection', backref='lesson', lazy=True, cascade="all, delete-orphan")

class LessonSection(db.Model):
    __tablename__ = 'lesson_sections'
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.String(50), db.ForeignKey('lessons.id'), nullable=False)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, default='')
    quiz_id = db.Column(db.String(50), db.ForeignKey('quizzes.id'), nullable=True)

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.Text, nullable=False)
    questions = db.relationship('QuizQuestion', backref='quiz', lazy=True, cascade="all, delete-orphan")

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.String(50), db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text) # Stored as JSON string
    correct_option_index = db.Column(db.Integer)

class UserLessonProgress(db.Model):
    __tablename__ = 'user_lesson_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.String(50), db.ForeignKey('lessons.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    last_accessed_at = db.Column(db.DateTime, default=datetime.utcnow)

class LearningQuestion(db.Model):
    __tablename__ = 'learning_questions'
    id = db.Column(db.Integer, primary_key=True)
    skill_type = db.Column(db.Text, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    reference_answer = db.Column(db.Text)
    keywords = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    attempts = db.relationship('UserAttempt', backref='learning_question', lazy=True)

class TestQuestion(db.Model):
    __tablename__ = 'test_questions'
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.Text, nullable=False)
    task_type = db.Column(db.Text, nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    reference_answer = db.Column(db.Text)
    keywords = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserAttempt(db.Model):
    __tablename__ = 'user_attempts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    learning_question_id = db.Column(db.Integer, db.ForeignKey('learning_questions.id'), nullable=True) # Made nullable for flexibility
    question_type = db.Column(db.String(50)) 
    question_id = db.Column(db.String(50)) 
    user_input = db.Column(db.Text, nullable=False)
    ai_feedback = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TestSession(db.Model):
    __tablename__ = 'test_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_score = db.Column(db.Float, nullable=False)
    ai_feedback = db.Column(db.Text, nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)

class TestAnswer(db.Model):
    __tablename__ = 'test_answers'
    id = db.Column(db.Integer, primary_key=True)
    test_session_id = db.Column(db.Integer, db.ForeignKey('test_sessions.id'), nullable=False)
    section = db.Column(db.Text, nullable=False)
    task_type = db.Column(db.Text, nullable=False)
    combined_question_ids = db.Column(db.Text, nullable=False)
    user_inputs = db.Column(db.Text, nullable=False)
    ai_feedback = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OCRTranslation(db.Model):
    __tablename__ = 'ocr_translations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    translated_and_explained = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- Initialization Functions ---

def create_database():
    """Create the database if it doesn't exist"""
    try:
        uri = Config.SQLALCHEMY_DATABASE_URI
        parsed = urlparse(uri)
        connection = pymysql.connect(
            host=parsed.hostname,
            port=parsed.port,
            user=parsed.username,
            password=parsed.password,
            charset='utf8mb4'
        )
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{parsed.path[1:]}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"Database '{parsed.path[1:]}' created or already exists")
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        return False
    return True

def create_tables():
    """Create all tables using SQLAlchemy"""
    try:
        with app.app_context():
            db.create_all()
            print("All tables created successfully")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Created tables: {', '.join(tables)}")
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False
    return True

def populate_sample_data():
    """Populate tables with sample data"""
    try:
        with app.app_context():
            # Check if Lessons already exist to avoid duplication
            # Note: For development/testing of this script, you might want to remove this check or clear DB
            # if Lesson.query.first():
            #    print("Lesson data already exists. Skipping population.")
            #    return True

            print("Populating Quizzes and Lessons...")

            # --- 1. Create Quizzes & Questions ---
            quizzes_data = [
                # Speaking Quizzes
                ('q1', 'Speaking Basics Quiz', [
                    ('How many parts are there in the Speaking test?', ['1', '2', '3', '4'], 2),
                    ('How long does the Speaking test last?', ['4-5 minutes', '11-14 minutes', '30 minutes', '1 hour'], 1)
                ]),
                ('q_s2', 'Speaking Part 2 Strategies Quiz', [
                    ('What is the best way to use the 1-minute preparation time?', ['Write full sentences', 'Write nothing', 'Write keywords and structure', 'Memorize a script'], 2),
                    ('Which structure is recommended for the long turn?', ['Past -> Present -> Future', 'Random thoughts', 'Just the conclusion', 'Only the present'], 0)
                ]),
                ('q_s3', 'Speaking Part 1 Topics Quiz', [
                    ('Which topic is NOT common in Part 1?', ['Hometown', 'Work/Studies', 'Nuclear Physics', 'Hobbies'], 2),
                    ('How should you answer Part 1 questions?', ['With one word', 'With natural, full sentences', 'With a prepared speech', 'By asking the examiner questions'], 1)
                ]),
                ('q_s4', 'Fluency & Coherence Quiz', [
                    ('What are "fillers"?', ['Words to waste time', 'Natural pauses like "Well..."', 'Silent moments', 'Incorrect grammar'], 1),
                    ('How can you improve coherence?', ['Speak very fast', 'Use linking words', 'Shout', 'Repeat the same word'], 1)
                ]),
                # Writing Quizzes
                ('q_w1', 'Writing Task 1 Quiz', [
                    ('What does a bar chart show?', ['A process', 'Comparison between categories', 'Locations on a map', 'A story'], 1),
                    ('Which word indicates an upward trend?', ['Decrease', 'Plummet', 'Increase', 'Stabilize'], 2)
                ]),
                ('q_w2', 'Writing Task 2 Quiz', [
                    ('How many paragraphs should a standard essay have?', ['1', '2', '4-5', '10'], 2),
                    ('Where should the thesis statement be?', ['In the conclusion', 'In the introduction', 'In body paragraph 1', 'Nowhere'], 1)
                ]),
                ('q_w3', 'Letter Writing Quiz', [
                    ('How do you start a formal letter?', ['Hi mate,', 'Dear Sir/Madam,', 'Hey there,', 'Yo,'], 1),
                    ('What is the tone for a letter to a friend?', ['Formal', 'Academic', 'Informal', 'Aggressive'], 2)
                ]),
                ('q_w4', 'Writing Vocabulary Quiz', [
                    ('Which is a linking word?', ['Apple', 'However', 'Run', 'Big'], 1),
                    ('Why use academic vocabulary?', ['To sound confusing', 'To boost your score', 'To annoy the examiner', 'It is not necessary'], 1)
                ]),
                # Listening Quizzes
                ('q_li1', 'Listening Details Quiz', [
                    ('What should you listen for?', ['General vibes', 'Specific details like names/numbers', 'Background noise', 'The examiner\'s accent'], 1),
                    ('Is spelling important?', ['No', 'Yes, very important', 'Only sometimes', 'Who knows?'], 1)
                ]),
                ('q_li2', 'Predicting Answers Quiz', [
                    ('What can help you predict the answer?', ['Grammar clues & context', 'Guessing randomly', 'Closing your eyes', 'Ignoring the audio'], 0),
                    ('If you see "a" before a blank, the answer is usually:', ['Plural noun', 'Singular noun', 'Verb', 'Adjective'], 1)
                ]),
                ('q_li3', 'Listening Accents Quiz', [
                    ('Which accent emphasizes the "r" sound?', ['British', 'Australian', 'American', 'None'], 2),
                    ('Why practice different accents?', ['To become an actor', 'To be prepared for variety in the test', 'It is fun', 'No reason'], 1)
                ]),
                ('q_li4', 'Map Labeling Quiz', [
                    ('What language is key for maps?', ['Colors', 'Directional (North, South, etc.)', 'Food', 'Emotion'], 1),
                    ('Where is "North" usually on a map?', ['Top', 'Bottom', 'Left', 'Right'], 0)
                ]),
                # Reading Quizzes
                ('q_r1', 'Skimming Quiz', [
                    ('What is skimming?', ['Reading every word', 'Reading for main ideas', 'Skipping the text', 'Reading aloud'], 1),
                    ('Where is the main idea often found?', ['Middle of paragraph', 'First/Last sentences', 'Footnotes', 'Title only'], 1)
                ]),
                ('q_r2', 'Scanning Quiz', [
                    ('What are you looking for when scanning?', ['General understanding', 'Specific keywords (names, dates)', 'Grammar mistakes', 'Funny jokes'], 1),
                    ('Do you need to read every word to scan?', ['Yes', 'No', 'Maybe', 'Always'], 1)
                ]),
                ('q_r3', 'T/F/NG Quiz', [
                    ('What does "False" mean?', ['Not mentioned', 'Opposite of text', 'Same as text', 'Confusing'], 1),
                    ('What does "Not Given" mean?', ['Information is missing', 'Information is wrong', 'Information is correct', 'Information is a lie'], 0)
                ]),
                ('q_r4', 'Matching Headings Quiz', [
                   ('What should you focus on?', ['Small details', 'Main idea of the paragraph', 'The first word', 'The length of the paragraph'], 1),
                   ('Are keywords always reliable?', ['Yes', 'No, they can be synonyms', 'Always', 'Never'], 1)
                ])
            ]

            for q_id, q_title, q_questions in quizzes_data:
                quiz = Quiz(id=q_id, title=q_title)
                db.session.merge(quiz)
                # Clear existing questions if re-running/updating
                QuizQuestion.query.filter_by(quiz_id=q_id).delete()
                for q_text, q_opts, q_correct in q_questions:
                    db.session.add(QuizQuestion(
                        quiz_id=q_id,
                        question_text=q_text,
                        options=json.dumps(q_opts),
                        correct_option_index=q_correct
                    ))

            # --- 2. Create Lessons ---
            # Helper to create lesson with section
            def create_lesson(lid, title, desc, cat, dur, sections_data):
                lesson = Lesson(id=lid, title=title, description=desc, category=cat, duration_minutes=dur)
                db.session.merge(lesson)
                # We delete old sections for simplicity in this dev script
                LessonSection.query.filter_by(lesson_id=lid).delete()
                for sec_title, sec_content, sec_quiz in sections_data:
                    db.session.add(LessonSection(lesson_id=lid, title=sec_title, content=sec_content, quiz_id=sec_quiz))

            # SPEAKING
            create_lesson('1', 'Introduction to IELTS Speaking', 'Learn the basics of the Speaking test format.', 'Speaking', 15, [
                ('Overview', 'The IELTS Speaking test consists of 3 parts and lasts 11-14 minutes. It is a face-to-face interview with an examiner.', None),
                ('Part 1: Introduction', 'General questions about yourself.', None),
                ('Part 2: Long Turn', 'Speak on a topic for 1-2 minutes.', None),
                ('Quiz: Speaking Basics', 'Test your knowledge.', 'q1')
            ])
            create_lesson('s2', 'Speaking Part 2 Strategies', 'Master the "Long Turn" with effective note-taking.', 'Speaking', 15, [
                ('Preparation', 'Use the 1 minute wisely for keywords.', None),
                ('Structure', 'Intro -> Past -> Present -> Future', None),
                ('Quiz: Strategies', 'Check understanding.', 'q_s2')
            ])
            create_lesson('s3', 'Common Topics in Speaking Part 1', 'Prepare for questions about home, work, and hobbies.', 'Speaking', 10, [
                ('Home & Hometown', 'Describe your living situation.', None),
                ('Work & Studies', 'Vocabulary for your occupation.', None),
                ('Quiz: Topics', 'Review common topics.', 'q_s3')
            ])
            create_lesson('s4', 'Improving Fluency & Coherence', 'Speak naturally without too many pauses.', 'Speaking', 20, [
                ('Fillers', 'Use "Actually", "Well" instead of silence.', None),
                ('Linking', 'Connect ideas logically.', None),
                ('Quiz: Fluency', 'Test fluency concepts.', 'q_s4')
            ])

            # WRITING
            create_lesson('2', 'Writing Task 1: Charts', 'How to describe bar charts effectively.', 'Writing', 25, [
                ('Understanding Charts', 'identify the main trends.', None),
                ('Vocabulary', 'Increase, decrease, remain steady.', None),
                ('Quiz: Charts', 'Test Task 1 skills.', 'q_w1')
            ])
            create_lesson('w2', 'Writing Task 2: Essay Structures', 'Organize your opinion or argument essays clearly.', 'Writing', 30, [
                ('Structure', '4 paragraphs: Intro, 2 Body, Conclusion.', None),
                ('Thesis', 'State opinion clearly.', None),
                ('Quiz: Essays', 'Review structure.', 'q_w2')
            ])
            create_lesson('w3', 'Letter Writing (General Training)', 'Formal vs Informal letters.', 'Writing', 20, [
                ('Formal', 'Dear Sir/Madam, Yours faithfully.', None),
                ('Informal', 'Hi John, Best wishes.', None),
                ('Quiz: Letters', 'Check letter styles.', 'q_w3')
            ])
            create_lesson('w4', 'Vocabulary for Writing', 'Academic words to boost your score.', 'Writing', 15, [
                ('Linking Words', 'Furthermore, However.', None),
                ('Lexical Resource', 'Use precise vocabulary.', None),
                ('Quiz: Vocab', 'Vocabulary check.', 'q_w4')
            ])

            # LISTENING
            create_lesson('3', 'Listening for Details', 'Techniques to catch specific information.', 'Listening', 20, [
                ('Focus', 'Listen for names, numbers, places.', None),
                ('Quiz: Details', 'Test detail listening.', 'q_li1')
            ])
            create_lesson('l2', 'Predicting Answers', 'Use context to guess the type of word needed.', 'Listening', 20, [
                ('Context Clues', 'Grammar helps predict noun/verb.', None),
                ('Quiz: Prediction', 'Prediction skills.', 'q_li2')
            ])
            create_lesson('l3', 'Listening to Accents', 'Familiarize with British, Australian, and American accents.', 'Listening', 15, [
                ('Varieties', 'Note differences in vowel sounds and "r".', None),
                ('Quiz: Accents', 'Accent knowledge.', 'q_li3')
            ])
            create_lesson('l4', 'Map Labeling', 'Navigating directions in Listening Section 2.', 'Listening', 25, [
                ('Directions', 'North, South, next to, opposite.', None),
                ('Quiz: Maps', 'Map skills.', 'q_li4')
            ])

            # READING
            create_lesson('4', 'Reading Skimming Techniques', 'Read faster and find answers quicker.', 'Reading', 30, [
                ('Skimming', 'Read first/last sentences for gist.', None),
                ('Quiz: Skimming', 'Skimming check.', 'q_r1')
            ])
            create_lesson('r2', 'Scanning for Keywords', 'Locate information without reading every word.', 'Reading', 15, [
                ('Scanning', 'Look for capital letters, numbers.', None),
                ('Quiz: Scanning', 'Scanning check.', 'q_r2')
            ])
            create_lesson('r3', 'True, False, Not Given', 'Strategies to handle this tricky question type.', 'Reading', 25, [
                ('Logic', 'False = Contradiction, NG = Missing.', None),
                ('Quiz: T/F/NG', 'Logic check.', 'q_r3')
            ])
            create_lesson('r4', 'Matching Headings', 'Match the correct heading to paragraphs.', 'Reading', 20, [
                ('Headings', 'Summarize the main idea.', None),
                ('Quiz: Headings', 'Heading check.', 'q_r4')
            ])

            db.session.commit()
            print("Populated lessons and quizzes.")
            
            # --- 3. Populate Test Questions (Writing & Speaking) ---
            # 20 Test Questions (10 Speaking, 10 Writing)
            test_questions_data = [
                # Speaking Part 1
                ('Speaking', 'Part 1', 'What is your favorite color and why?', 'Personal preference, simple justification.', 'Red, Blue, cheerful, calm'),
                ('Speaking', 'Part 1', 'Do you work or are you a student?', 'State current status clearly.', 'Student, Work, University, Job'),
                ('Speaking', 'Part 1', 'How often do you use a computer?', 'Frequency phrases.', 'Every day, Rarely, For work'),
                ('Speaking', 'Part 1', 'Do you like to travel?', 'Opinion + reason.', 'Yes, explore, culture, No, homebody'),
                # Speaking Part 2
                ('Speaking', 'Part 2', 'Describe a book you recently read. You should say: what it was, who wrote it, what it was about, and explain why you liked it.', 'Past tense narrative, description.', 'Novel, Author, Plot, Interesting'),
                ('Speaking', 'Part 2', 'Describe a gift you gave to someone. You should say: what the gift was, who you gave it to, why you chose it, and how they reacted.', 'Past tense, emotions.', 'Present, Surprise, Happy'),
                ('Speaking', 'Part 2', 'Describe a healthy habit you have. You should say: what it is, when you do it, how it helps you, and if you would recommend it.', 'Present simple, health vocab.', 'Exercise, Diet, Meditation'),
                # Speaking Part 3
                ('Speaking', 'Part 3', 'Do you think people today read enough books?', 'Abstract opinion, comparison.', 'Digital era, decline, knowledge'),
                ('Speaking', 'Part 3', 'Is gift-giving important in your culture?', 'Cultural norms, values.', 'Tradition, Respect, Relationships'),
                ('Speaking', 'Part 3', 'How can governments encourage healthy lifestyles?', 'Suggestions, policy.', 'Tax sugar, Parks, Education'),

                # Writing Task 1
                ('Writing', 'Task 1', 'The chart below shows the number of tourists visiting three different countries from 1995 to 2010. Summarize the information explicitly.', 'Comparison, trends, past tense.', 'Increase, Decrease, Fluctuate, Peak'),
                ('Writing', 'Task 1', 'The diagram illustrates the process of making chocolate. Summarize the steps.', 'Passive voice, sequence connectors.', 'First, Then, Finally, Harvested, Processed'),
                ('Writing', 'Task 1', 'The table compares the cost of water in 5 major cities in 2023.', 'Superlatives, comparatives.', 'Highest, Lowest, More expensive'),
                ('Writing', 'Task 1', 'The map shows the changes in a village park between 2010 and 2020.', 'Location prepositions, change verbs.', 'Built, Demolished, Expanded'),
                # Writing Task 2
                ('Writing', 'Task 2', 'Some people believe that the internet has brought people closer together, while others think it has made us more isolated. Discuss both views and give your opinion.', 'Discussion, balance.', 'Communication, Social media, loneliness'),
                ('Writing', 'Task 2', 'Education should be free for everyone. To what extent do you agree or disagree?', 'Argumentative, modals.', 'University, Cost, Opportunity, Tax'),
                ('Writing', 'Task 2', 'Environmental problems are too big for individuals to solve. Only governments can handle them. Do you agree?', 'Agree/Disagree, environment.', 'Responsibility, Policy, Recycling'),
                ('Writing', 'Task 2', 'In many countries, people are living longer. What are the advantages and disadvantages of this trend?', 'Pros/Cons.', 'Healthcare, Pension, Experience, Burden'),
                ('Writing', 'Task 2', 'Children should be taught to manage money at school. Do you agree?', 'Education, life skills.', 'Curriculum, Finance, Future'),
                ('Writing', 'Task 2', 'Should public transport be free? Discuss.', 'Opinion, urban planning.', 'Traffic, Pollution, Cost, Tax')
            ]

            if not TestQuestion.query.first():
                 print("Populating Test Questions...")
                 for sec, t_type, prompt, ans, keys in test_questions_data:
                     db.session.add(TestQuestion(
                         section=sec,
                         task_type=t_type,
                         prompt=prompt,
                         reference_answer=ans,
                         keywords=keys
                     ))
                 db.session.commit()
                 print("Test Questions populated.")
            else:
                 # Check if we need to add these specific ones (simple check: count)
                 count = TestQuestion.query.count()
                 if count < 20: 
                      print("Adding missing Test Questions...")
                      # Clear and re-add for simplicity in dev/init script
                      TestQuestion.query.delete()
                      for sec, t_type, prompt, ans, keys in test_questions_data:
                           db.session.add(TestQuestion(
                               section=sec,
                               task_type=t_type,
                               prompt=prompt,
                               reference_answer=ans,
                               keywords=keys
                           ))
                      db.session.commit()
                      print("Test Questions updated.")

    except Exception as e:
        print(f"Error populating sample data: {e}")
        db.session.rollback()
        return False
    return True

def main():
    print("Initializing Database...")
    if not create_database(): return
    if not create_tables(): return
    if not populate_sample_data(): return
    print("\n✅ Database initialization completed successfully!")

if __name__ == "__main__":
    main()
