#!/usr/bin/env python3
"""
Test runner for TOEFL Learning API
This script properly sets up the Python path and runs tests
"""

import sys
import os
import subprocess

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def run_api_tests():
    """Run API integration tests"""
    print("🧪 Running API Tests...")
    try:
        result = subprocess.run([
            sys.executable, 
            os.path.join(project_root, 'tests', 'test_api.py')
        ], cwd=project_root, capture_output=True, text=True)
        
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running API tests: {e}")
        return False

def run_mysql_tests():
    """Run MySQL connection tests"""
    print("🧪 Running MySQL Tests...")
    try:
        result = subprocess.run([
            sys.executable, 
            os.path.join(project_root, 'tests', 'test_mysql.py')
        ], cwd=project_root, capture_output=True, text=True)
        
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running MySQL tests: {e}")
        return False

def test_imports():
    """Test that all modules can be imported correctly"""
    print("🔍 Testing imports...")
    
    try:
        # Test main app creation
        from app import create_app
        app = create_app()
        print("✅ Main app factory works")
        
        # Test database models
        from app.models.database import db, User, LearningQuestion, TestQuestion
        print("✅ Database models import successfully")
        
        # Test utilities
        from app.utils.helpers import hash_password, get_learning_questions_by_level
        print("✅ Utility functions import successfully")
        
        # Test routes
        from app.routes.auth import auth_bp
        from app.routes.learning import learning_bp
        from app.routes.test import test_bp
        from app.routes.ocr import ocr_bp
        from app.routes.user import user_bp
        from app.routes.question import question_bp
        print("✅ All route blueprints import successfully")
        
        # Test AI models
        from app.ai_models.alysa import ai_toefl_feedback as alysa_feedback
        from app.ai_models.gemini import ai_toefl_feedback as gemini_feedback
        from app.ai_models.ocr import process_image
        print("✅ AI models import successfully")
        
        print(f"✅ App has {len(app.blueprints)} registered blueprints")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting TOEFL Learning API Test Suite")
    print("=" * 50)
    
    # Test imports first
    import_success = test_imports()
    
    if not import_success:
        print("❌ Import tests failed. Cannot continue with other tests.")
        return False
    
    print("\n" + "=" * 50)
    
    # Run other tests
    api_success = run_api_tests()
    mysql_success = run_mysql_tests()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Imports: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"   API Tests: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"   MySQL Tests: {'✅ PASS' if mysql_success else '❌ FAIL'}")
    
    all_passed = import_success and api_success and mysql_success
    print(f"\n🎯 Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
