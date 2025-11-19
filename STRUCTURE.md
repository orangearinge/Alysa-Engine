# TOEFL Learning API - Organized Project Structure

## 📁 Project Structure

```
alysa-engine/
├── 📄 app.py                    # Main application entry point
├── 📄 config.py                 # Application configuration
├── 📄 init_db.py               # Database initialization script
├── 📄 requirements.txt         # Python dependencies
├── 📄 README.md                # Main project documentation
├── 📄 STRUCTURE_README.md      # This file - structure documentation
├── 📄 REFACTOR_README.md       # Refactoring history
├── 📄 database-structure.md    # Database schema documentation
│
├── 📁 app/                     # Main application package
│   ├── 📄 __init__.py          # App factory and configuration
│   │
│   ├── 📁 models/              # Database models
│   │   ├── 📄 __init__.py
│   │   └── 📄 database.py      # All SQLAlchemy models
│   │
│   ├── 📁 routes/              # API route blueprints
│   │   ├── 📄 __init__.py
│   │   ├── 📄 auth.py          # Authentication endpoints
│   │   ├── 📄 learning.py      # Learning mode endpoints
│   │   ├── 📄 test.py          # TOEFL test simulation endpoints
│   │   ├── 📄 ocr.py           # OCR translation endpoints
│   │   ├── 📄 user.py          # User history endpoints
│   │   └── 📄 question.py      # Question management endpoints
│   │
│   ├── 📁 utils/               # Utility functions
│   │   ├── 📄 __init__.py
│   │   ├── 📄 helpers.py       # General helper functions
│   │   └── 📄 ocr.py           # OCR processing utilities
│   │
│   └── 📁 ai_models/           # AI feedback models
│       ├── 📄 __init__.py
│       ├── 📄 alysa.py         # Alysa AI feedback model
│       └── 📄 gemini.py        # Gemini AI feedback model
│
├── 📁 tests/                   # Test files
    ├── 📄 __init__.py
    ├── 📄 test_api.py          # API endpoint tests
    ├── 📄 test_mysql.py        # Database tests
    └── 📄 test_routes.py       # Route-specific tests

```

## 🏗️ Architecture Overview

### **Application Factory Pattern**
- `app/__init__.py` contains the `create_app()` factory function
- Proper extension initialization and blueprint registration
- Configuration management centralized

### **Blueprint-Based Routing**
Each route module is organized by functionality:

- **`auth.py`** - User registration and login
- **`learning.py`** - Learning mode with AI feedback
- **`test.py`** - TOEFL iBT test simulation (6 tasks)
- **`ocr.py`** - Image OCR and translation
- **`user.py`** - User history and progress tracking
- **`question.py`** - Question management and retrieval

### **Model Layer**
- `app/models/database.py` contains all SQLAlchemy models:
  - `User` - User accounts and authentication
  - `LearningQuestion` - Practice questions for learning mode
  - `TestQuestion` - TOEFL iBT test questions
  - `UserAttempt` - Learning mode submissions and feedback
  - `TestSession` - TOEFL test sessions
  - `TestAnswer` - Individual task answers in test mode
  - `OCRTranslation` - OCR processing history

### **Utility Layer**
- `app/utils/helpers.py` - Password hashing and question queries
- `app/utils/ocr.py` - Image processing and OCR functionality

### **AI Models Layer**
- `app/ai_models/alysa.py` - Alysa AI feedback model
- `app/ai_models/gemini.py` - Gemini AI feedback model
- Both models support learning and test modes

## 🚀 Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database (first time only)
python3 init_db.py

# Run the application
python3 app.py
```

## 📡 API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login

### Learning Mode
- `GET /api/learning/questions` - Get practice questions
- `POST /api/learning/submit` - Submit answers for feedback

### Test Mode (TOEFL iBT)
- `POST /api/test/start` - Start test session (6 tasks)
- `POST /api/test/submit` - Submit test answers for evaluation

### OCR Translation
- `POST /api/ocr/translate` - Upload image for OCR and translation

### User History
- `GET /api/user/attempts` - Get learning attempts history
- `GET /api/user/test-sessions` - Get test sessions history
- `GET /api/user/ocr-history` - Get OCR translation history

### Question Management
- `GET /api/questions/learning` - Get all learning questions
- `GET /api/questions/test` - Get all test questions

### Health Check
- `GET /api/health` - API health status

## 🔧 Key Benefits of New Structure

### **1. Maintainability**
- Clear separation of concerns
- Easy to locate and modify specific functionality
- Reduced code duplication

### **2. Scalability**
- Easy to add new routes or models
- Modular architecture supports team development
- Clean import structure

### **3. Testability**
- Individual modules can be tested separately
- Clear dependencies between components
- Test files organized in dedicated directory

### **4. Code Organization**
- Related functionality grouped together
- Consistent naming conventions
- Proper Python package structure

### **5. Development Experience**
- Better IDE support and autocomplete
- Easier debugging and error tracking
- Clear project navigation

## 🔄 Migration Notes

- **No Logic Changes** - All existing functionality preserved
- **Same API Contract** - All endpoints work exactly the same
- **Database Compatibility** - No schema changes required
- **Backward Compatible** - Existing clients continue to work

## 🧪 Testing

```bash
# Run all tests
python3 -m pytest tests/

# Run specific test file
python3 tests/test_api.py
```

## 📝 Development Guidelines

1. **Adding New Routes**: Create new blueprint files in `app/routes/`
2. **Adding Models**: Add to `app/models/database.py`
3. **Adding Utilities**: Add to appropriate file in `app/utils/`
4. **Adding Tests**: Create test files in `tests/` directory
5. **Import Convention**: Always use absolute imports from `app.` package
