# IELTS Learning Dataset - Summary

## Dataset Overview
Created comprehensive IELTS learning datasets in CSV format following IELTS standards and pedoman.md guidelines.

## Files Created

### 1. alysa_lessons.csv
**Total: 20 lessons** (5 per section)
- **Speaking (sp1-sp5)**: Fluency & Coherence, Pronunciation & Intonation, Lexical Resource, Grammatical Range, Part 2 Cue Card Mastery
- **Writing (wr1-wr5)**: Task Achievement, Coherence & Cohesion, Lexical Resource, Grammatical Range, Essay Types
- **Listening (li1-li5)**: Specific Information, Main Ideas, Directions & Maps, Note Completion, Multiple Choice
- **Reading (re1-re5)**: Skimming, Scanning, True/False/Not Given, Matching Headings, Summary Completion

**Columns**: id, title, description, category, duration_minutes, created_at

### 2. alysa_lesson_sections.csv
**Total: 60 lesson sections** (3 content sections per lesson)
- Each lesson has 3 detailed content sections
- Content follows IELTS best practices
- Includes explanations, examples, and practical tips
- Last section of each lesson links to quiz

**Columns**: id, lesson_id, title, content, quiz_id

**Content Structure per Lesson**:
- Section 1: Introduction to concept
- Section 2: Detailed explanation with examples
- Section 3: Practical application + Quiz link

### 3. alysa_quizzes.csv
**Total: 20 quizzes** (1 per lesson)
- quiz_sp1 to quiz_sp5 (Speaking)
- quiz_wr1 to quiz_wr5 (Writing)
- quiz_li1 to quiz_li5 (Listening)
- quiz_re1 to quiz_re5 (Reading)

**Columns**: id, title

### 4. alysa_quiz_questions.csv
**Total: 60 quiz questions** (3 questions per quiz)
- Multiple choice format with 4 options
- Tests understanding of lesson content
- Covers key concepts from each lesson
- Correct answer index provided (0-3)

**Columns**: id, quiz_id, question_text, options, correct_option_index

### 5. alysa_test_questions.csv
**Total: 30 test questions**

#### Speaking Questions (15 total):
- **Part 1 (8 questions)**: Work/Study, Free time, Preferences, Social media, etc.
- **Part 2 (7 questions)**: Cue card topics with bullet points
  - Job/Field of study
  - Influential person
  - Place to visit
  - Skill to learn
  - Memorable event
  - Book/Film
  - Future goal

#### Writing Questions (15 total):
- **All Task 2 essays** covering various types:
  - Opinion/Agree-Disagree (5 questions)
  - Discussion (5 questions)
  - Advantages-Disadvantages (2 questions)
  - Problem-Solution (1 question)
  - Cause-Effect (1 question)
  - Two-part questions (1 question)

**Topics covered**: Education, Technology, Work, Environment, Society, Crime, Family, Success, etc.

**Columns**: id, section, task_type, prompt, reference_answer, keywords, created_at

## Dataset Statistics

| Category | Lessons | Sections | Quizzes | Quiz Questions | Test Questions |
|----------|---------|----------|---------|----------------|----------------|
| Speaking | 5 | 15 | 5 | 15 | 15 (Part 1 & 2) |
| Writing | 5 | 15 | 5 | 15 | 15 (Task 2) |
| Listening | 5 | 15 | 5 | 15 | 0 |
| Reading | 5 | 15 | 5 | 15 | 0 |
| **TOTAL** | **20** | **60** | **20** | **60** | **30** |

## Content Quality Features

### Learning Content (Lessons & Sections)
✅ Based on official IELTS assessment criteria
✅ Covers all four skills comprehensively
✅ Includes practical examples and tips
✅ Progressive difficulty within each section
✅ Clear explanations with do's and don'ts
✅ Real IELTS scenarios and common mistakes

### Quiz Questions
✅ 3 questions per lesson for knowledge check
✅ Multiple choice format (4 options)
✅ Tests key concepts from lesson content
✅ Varied difficulty levels
✅ Clear correct answers provided

### Test Questions
✅ Authentic IELTS question formats
✅ Speaking: Part 1 (short answers) and Part 2 (long turn with cue cards)
✅ Writing: Task 2 essays only (opinion, discussion, problem-solution, etc.)
✅ Detailed reference answers provided
✅ Keywords for assessment included
✅ Covers diverse topics relevant to IELTS

## IELTS Standards Compliance

All content follows official IELTS guidelines:
- **Speaking**: Fluency & Coherence, Lexical Resource, Grammatical Range & Accuracy, Pronunciation
- **Writing**: Task Achievement, Coherence & Cohesion, Lexical Resource, Grammatical Range & Accuracy
- **Listening**: Understanding main ideas, specific information, speaker opinions, attitudes
- **Reading**: Skimming, scanning, detailed reading, understanding logical argument

## Usage Notes

1. **For Learning Module**: Use lessons → lesson_sections → quizzes → quiz_questions
2. **For Testing Module**: Use test_questions directly
3. **Quiz Integration**: Each lesson's 3rd section links to corresponding quiz via quiz_id
4. **Test Difficulty**: Speaking questions range from Part 1 (easier) to Part 2 (more complex); Writing Task 2 questions vary by essay type

## File Locations
All CSV files are located in: `/home/ahmadsaif/project/bank materi and soal alysa/`

- alysa_lessons.csv
- alysa_lesson_sections.csv
- alysa_quizzes.csv
- alysa_quiz_questions.csv
- alysa_test_questions.csv

---
**Created**: 2026-01-16
**Format**: CSV (Comma-Separated Values)
**Encoding**: UTF-8
**Total Records**: 190 across all files
