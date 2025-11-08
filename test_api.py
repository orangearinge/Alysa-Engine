#!/usr/bin/env python3
"""
API Testing Script for TOEFL Learning System
Run this script to test all API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

class APITester:
    def __init__(self):
        self.access_token = None
        self.session = requests.Session()
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def print_response(self, response, endpoint_name):
        """Print formatted response"""
        print(f"\n{'='*50}")
        print(f"Testing: {endpoint_name}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print(f"{'='*50}")
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.session.get(f"{BASE_URL}/health")
        self.print_response(response, "Health Check")
        return response.status_code == 200
    
    def test_register(self):
        """Test user registration"""
        data = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "password123"
        }
        
        response = self.session.post(f"{BASE_URL}/register", json=data)
        self.print_response(response, "User Registration")
        
        if response.status_code == 201:
            self.access_token = response.json().get('access_token')
            self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
            return True
        return False
    
    def test_login(self):
        """Test user login (using existing user)"""
        data = {
            "username": "testuser",
            "password": "password123"
        }
        
        response = self.session.post(f"{BASE_URL}/login", json=data)
        self.print_response(response, "User Login")
        
        if response.status_code == 200:
            self.access_token = response.json().get('access_token')
            self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
            return True
        return False
    
    def test_learning_questions(self):
        """Test get learning questions"""
        response = self.session.get(f"{BASE_URL}/learning/questions")
        self.print_response(response, "Get Learning Questions")
        return response.status_code == 200
    
    def test_learning_submit(self):
        """Test submit learning answer"""
        data = {
            "question_id": 1,
            "answer": "My hometown is Jakarta, the capital city of Indonesia. It is a vibrant metropolis with rich culture and delicious food. The people are friendly and welcoming to visitors.",
            "model": "gemini"
        }
        
        response = self.session.post(f"{BASE_URL}/learning/submit", json=data)
        self.print_response(response, "Submit Learning Answer")
        return response.status_code == 200
    
    def test_start_test(self):
        """Test start test session"""
        data = {
            "section": "writing",
            "task_types": ["independent", "integrated"]
        }
        response = self.session.post(f"{BASE_URL}/test/start", json=data)
        self.print_response(response, "Start Test Session")
        
        if response.status_code == 200:
            return response.json().get('session_id')
        return None
    
    def test_submit_test(self, session_id):
        """Test submit test answers using new task-based structure"""
        data = {
            "session_id": session_id,
            "task_answers": [
                {
                    "task_type": "independent",
                    "section": "writing",
                    "answers": [
                        {
                            "question_id": 1,
                            "answer": "I prefer to study alone because it allows me to focus better and learn at my own pace. When studying alone, I can choose the environment and methods that work best for me."
                        }
                    ]
                },
                {
                    "task_type": "integrated",
                    "section": "writing",
                    "answers": [
                        {
                            "question_id": 3,
                            "answer": "The reading passage discusses the benefits of renewable energy sources, including environmental protection and economic advantages. The lecture supports these points by providing specific examples of successful renewable energy implementations in various countries."
                        }
                    ]
                }
            ]
        }
        
        response = self.session.post(f"{BASE_URL}/test/submit", json=data)
        self.print_response(response, "Submit Test Answers")
        return response.status_code == 200
    
    def test_user_attempts(self):
        """Test get user attempts"""
        response = self.session.get(f"{BASE_URL}/user/attempts")
        self.print_response(response, "Get User Attempts")
        return response.status_code == 200
    
    def test_user_test_sessions(self):
        """Test get user test sessions"""
        response = self.session.get(f"{BASE_URL}/user/test-sessions")
        self.print_response(response, "Get User Test Sessions")
        return response.status_code == 200
    
    def run_all_tests(self):
        """Run all API tests"""
        print("Starting API Tests for TOEFL Learning System")
        print("=" * 60)
        
        tests_passed = 0
        total_tests = 0
        
        # Test 1: Health Check
        total_tests += 1
        if self.test_health_check():
            tests_passed += 1
            print("✅ Health Check - PASSED")
        else:
            print("❌ Health Check - FAILED")
        
        # Test 2: User Registration
        total_tests += 1
        if self.test_register():
            tests_passed += 1
            print("✅ User Registration - PASSED")
        else:
            print("❌ User Registration - FAILED")
            # Try login instead
            if self.test_login():
                print("✅ User Login (fallback) - PASSED")
        
        # Test 3: Learning Questions
        total_tests += 1
        if self.test_learning_questions():
            tests_passed += 1
            print("✅ Get Learning Questions - PASSED")
        else:
            print("❌ Get Learning Questions - FAILED")
        
        # Test 4: Submit Learning Answer
        total_tests += 1
        if self.test_learning_submit():
            tests_passed += 1
            print("✅ Submit Learning Answer - PASSED")
        else:
            print("❌ Submit Learning Answer - FAILED")
        
        # Test 5: Start Test Session
        total_tests += 1
        session_id = self.test_start_test()
        if session_id:
            tests_passed += 1
            print("✅ Start Test Session - PASSED")
            
            # Test 6: Submit Test Answers
            total_tests += 1
            if self.test_submit_test(session_id):
                tests_passed += 1
                print("✅ Submit Test Answers - PASSED")
            else:
                print("❌ Submit Test Answers - FAILED")
        else:
            print("❌ Start Test Session - FAILED")
            total_tests += 1  # Count the submit test as failed too
            print("❌ Submit Test Answers - SKIPPED")
        
        # Test 7: User Attempts
        total_tests += 1
        if self.test_user_attempts():
            tests_passed += 1
            print("✅ Get User Attempts - PASSED")
        else:
            print("❌ Get User Attempts - FAILED")
        
        # Test 8: User Test Sessions
        total_tests += 1
        if self.test_user_test_sessions():
            tests_passed += 1
            print("✅ Get User Test Sessions - PASSED")
        else:
            print("❌ Get User Test Sessions - FAILED")
        
        # Summary
        print("\n" + "=" * 60)
        print(f"TEST SUMMARY: {tests_passed}/{total_tests} tests passed")
        if tests_passed == total_tests:
            print("🎉 All tests passed! API is working correctly.")
        else:
            print(f"⚠️  {total_tests - tests_passed} tests failed. Check the output above.")
        print("=" * 60)

def main():
    """Main function"""
    print("TOEFL Learning System - API Tester")
    print("Make sure the Flask app is running on http://localhost:5000")
    print("Press Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nTest cancelled.")
        return
    
    tester = APITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
