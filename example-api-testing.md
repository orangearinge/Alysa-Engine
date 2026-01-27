# API Testing Documentation

## 2.3.2 API Testing

Tabel berikut memuat hasil pengujian untuk seluruh endpoint API yang tersedia pada aplikasi.

| No  | Endpoint                         | Metode HTTP | Data Diuji                                                                                             | Status (Pass/Fail) |
| --- | -------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------ | ------------------ |
| 1   | `/api/auth/firebase-login`       | POST        | Header: `Authorization: Bearer <firebase_token>`                                                       | Pass               |
| 2   | `/api/chatbot/chat`              | POST        | Body: `{"message": "Halo, apa kabar?"}`                                                                | Pass               |
| 3   | `/api/feedback`                  | POST        | Body: `{"feedback_text": "Aplikasi sangat membantu untuk belajar IELTS."}`                             | Pass               |
| 4   | `/api/lessons`                   | GET         | Params: `category=Speaking` (Optional)                                                                 | Pass               |
| 5   | `/api/lessons/<lesson_id>`       | GET         | Path Variable: `lesson_id=1`                                                                           | Pass               |
| 6   | `/api/quizzes/<quiz_id>`         | GET         | Path Variable: `quiz_id=q1`                                                                            | Pass               |
| 7   | `/api/learning/progress`         | POST        | Body: `{"lesson_id": "1", "is_completed": true}`                                                       | Pass               |
| 8   | `/api/ocr/translate`             | POST        | Form-Data: `image=<file_image>`, Header: `Authorization: Bearer <token>`                               | Pass               |
| 9   | `/api/user/ocr-history`          | GET         | Header: `Authorization: Bearer <token>`, Params: `page=1, per_page=10`                                 | Pass               |
| 10  | `/api/user/profile`              | GET         | Header: `Authorization: Bearer <token>`                                                                | Pass               |
| 11  | `/api/user/profile`              | PUT         | Body: `{"target_score": 7.5, "daily_study_time_minutes": 60}`, Header: `Authorization: Bearer <token>` | Pass               |
| 12  | `/api/user/attempts`             | GET         | Header: `Authorization: Bearer <token>`                                                                | Pass               |
| 13  | `/api/user/test-sessions`        | GET         | Header: `Authorization: Bearer <token>`                                                                | Pass               |
| 14  | `/api/test/start`                | POST        | Header: `Authorization: Bearer <token>`                                                                | Pass               |
| 15  | `/api/test/submit`               | POST        | Body: `{"session_id": 1, "task_answers": [...]}` (Data jawaban lengkap 6 task)                         | Pass               |
| 16  | `/api/test/practice/start`       | POST        | Header: `Authorization: Bearer <token>`                                                                | Pass               |
| 17  | `/api/test/practice/submit`      | POST        | Body: `{"session_id": 2, "answers": [{"question_id": 1, "answer": "I agree..."}]}`                     | Pass               |
| 18  | `/api/test/session/<session_id>` | GET         | Path Variable: `session_id=1`, Header: `Authorization: Bearer <token>`                                 | Pass               |
| 19  | `/api/admin/seed_content`        | POST        | None (Utility untuk seed database)                                                                     | Pass               |
