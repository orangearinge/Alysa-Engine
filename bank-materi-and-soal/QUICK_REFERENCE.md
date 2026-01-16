# 📊 IELTS Dataset - Quick Reference

## ✅ Files Created Successfully

| File Name | Records | Description |
|-----------|---------|-------------|
| `alysa_lessons.csv` | 20 | Main lessons (5 per skill) |
| `alysa_lesson_sections.csv` | 60 | Content sections (3 per lesson) |
| `alysa_quizzes.csv` | 20 | Quiz titles (1 per lesson) |
| `alysa_quiz_questions.csv` | 60 | Quiz questions (3 per quiz) |
| `alysa_test_questions.csv` | 30 | Test questions (15 Speaking + 15 Writing) |
| **TOTAL** | **190** | **Complete IELTS Learning Dataset** |

---

## 📚 Learning Content Structure

### Speaking Section (5 Lessons)
```
sp1: Fluency & Coherence
├── Section 1: What is Fluency?
├── Section 2: What is Coherence?
└── Section 3: Common Fluency Problems → Quiz (3 questions)

sp2: Pronunciation & Intonation
├── Section 1: Understanding Pronunciation
├── Section 2: Word Stress & Sentence Stress
└── Section 3: Intonation Patterns → Quiz (3 questions)

sp3: Lexical Resource in Speaking
├── Section 1: Using Varied Vocabulary
├── Section 2: Topic-Specific Vocabulary
└── Section 3: Idiomatic Expressions & Collocations → Quiz (3 questions)

sp4: Grammatical Range & Accuracy
├── Section 1: Using Complex Sentences
├── Section 2: Tense Accuracy
└── Section 3: Common Grammar Mistakes → Quiz (3 questions)

sp5: Part 2 Cue Card Mastery
├── Section 1: Understanding Part 2 Format
├── Section 2: Structuring Your Response
└── Section 3: Extension Techniques → Quiz (3 questions)
```

### Writing Section (5 Lessons)
```
wr1: Task Achievement in Writing
├── Section 1: Understanding Task 1 Requirements
├── Section 2: Understanding Task 2 Requirements
└── Section 3: Analyzing the Question → Quiz (3 questions)

wr2: Coherence & Cohesion in Writing
├── Section 1: Paragraph Structure
├── Section 2: Cohesive Devices
└── Section 3: Logical Organization → Quiz (3 questions)

wr3: Lexical Resource in Writing
├── Section 1: Academic Vocabulary
├── Section 2: Paraphrasing Skills
└── Section 3: Avoiding Repetition → Quiz (3 questions)

wr4: Grammatical Range in Writing
├── Section 1: Sentence Variety
├── Section 2: Advanced Grammar Structures
└── Section 3: Error-Free Writing → Quiz (3 questions)

wr5: Task 2 Essay Types
├── Section 1: Opinion Essays
├── Section 2: Discussion Essays
└── Section 3: Problem-Solution Essays → Quiz (3 questions)
```

### Listening Section (5 Lessons)
```
li1: Listening for Specific Information
├── Section 1: Listening for Names & Spelling
├── Section 2: Catching Numbers & Dates
└── Section 3: Identifying Specific Details → Quiz (3 questions)

li2: Understanding Main Ideas
├── Section 1: Understanding Context & Purpose
├── Section 2: Identifying Main Ideas
└── Section 3: Distinguishing Main vs Supporting Points → Quiz (3 questions)

li3: Following Directions & Maps
├── Section 1: Map Vocabulary & Directions
├── Section 2: Following Route Descriptions
└── Section 3: Labeling Maps & Plans → Quiz (3 questions)

li4: Note Completion Strategies
├── Section 1: Note Completion Strategy
├── Section 2: Form & Table Completion
└── Section 3: Sentence Completion Tips → Quiz (3 questions)

li5: Multiple Choice Techniques
├── Section 1: Multiple Choice Strategy
├── Section 2: Avoiding Distractors
└── Section 3: Managing Time in Multiple Choice → Quiz (3 questions)
```

### Reading Section (5 Lessons)
```
re1: Skimming for Main Ideas
├── Section 1: What is Skimming?
├── Section 2: Identifying Topic Sentences
└── Section 3: Finding Main Ideas Quickly → Quiz (3 questions)

re2: Scanning for Details
├── Section 1: What is Scanning?
├── Section 2: Scanning Techniques
└── Section 3: Using Keywords Effectively → Quiz (3 questions)

re3: True/False/Not Given Strategies
├── Section 1: Understanding True/False/Not Given
├── Section 2: Common Mistakes to Avoid
└── Section 3: Step-by-Step Approach → Quiz (3 questions)

re4: Matching Headings
├── Section 1: Understanding Heading Questions
├── Section 2: Identifying Paragraph Main Ideas
└── Section 3: Avoiding Heading Traps → Quiz (3 questions)

re5: Summary & Sentence Completion
├── Section 1: Summary Completion Strategy
├── Section 2: Sentence Completion Tips
└── Section 3: Maintaining Accuracy → Quiz (3 questions)
```

---

## 🎯 Test Questions Breakdown

### Speaking Test Questions (15 total)

#### Part 1 - Short Answers (8 questions)
1. Do you work or are you a student?
2. What do you like most about your job or studies?
3. Is there anything you would like to change?
4. Do you think your work/studies will change in the future?
5. What do you usually do in your free time?
6. Do you prefer to spend time alone or with friends?
7. What kind of music do you like?
8. How often do you use social media?

#### Part 2 - Long Turn with Cue Cards (7 questions)
1. Describe your job or field of study
2. Describe a person who has influenced you
3. Describe a place you like to visit
4. Describe a skill you would like to learn
5. Describe a memorable event in your life
6. Describe a book or film that you enjoyed
7. Describe a goal you have for the future

### Writing Test Questions (15 total)

#### Task 2 Essay Types:
- **Opinion/Agree-Disagree**: 5 questions
  - Financial education in schools
  - Technology and communication
  - Job mobility
  - Environmental responsibility
  - Success factors

- **Discussion (both views + opinion)**: 5 questions
  - University purpose (practical vs theoretical)
  - Early childhood education
  - Crime reduction methods
  - Teaching social values (parents vs school)
  - Acceptance vs improvement in life

- **Advantages-Disadvantages**: 2 questions
  - Aging population
  - Gap year before university

- **Problem-Solution**: 1 question
  - Consumer goods and environment

- **Cause-Effect**: 1 question
  - Declining birth rates

- **Two-part**: 1 question
  - Technology's impact on relationships

---

## 📋 CSV Format Details

### alysa_lessons.csv
```
id, title, description, category, duration_minutes, created_at
```

### alysa_lesson_sections.csv
```
id, lesson_id, title, content, quiz_id
```

### alysa_quizzes.csv
```
id, title
```

### alysa_quiz_questions.csv
```
id, quiz_id, question_text, options, correct_option_index
```
*Note: options is JSON array format: ["option1", "option2", "option3", "option4"]*

### alysa_test_questions.csv
```
id, section, task_type, prompt, reference_answer, keywords, created_at
```

---

## 🎓 IELTS Standards Compliance

All content follows official IELTS assessment criteria:

### Speaking
- ✅ Fluency & Coherence
- ✅ Lexical Resource
- ✅ Grammatical Range & Accuracy
- ✅ Pronunciation

### Writing
- ✅ Task Achievement (Task 1) / Task Response (Task 2)
- ✅ Coherence & Cohesion
- ✅ Lexical Resource
- ✅ Grammatical Range & Accuracy

### Listening
- ✅ Understanding main ideas
- ✅ Specific information
- ✅ Speaker opinions and attitudes
- ✅ Following directions

### Reading
- ✅ Skimming for gist
- ✅ Scanning for details
- ✅ Understanding logical argument
- ✅ Recognizing writer's views

---

## 💡 Usage Tips

1. **Import to Database**: Use these CSV files to populate your database tables
2. **Learning Flow**: Lessons → Lesson Sections → Quizzes → Quiz Questions
3. **Testing Flow**: Test Questions (direct access for practice tests)
4. **Quiz Integration**: Each lesson's 3rd section links to its quiz via `quiz_id`
5. **Encoding**: All files are UTF-8 encoded for proper character display

---

**Created**: January 16, 2026  
**Total Records**: 190  
**Format**: CSV (UTF-8)  
**Status**: ✅ Complete and Ready to Use
