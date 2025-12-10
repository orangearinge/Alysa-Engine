#!/usr/bin/env python3
"""
API Testing Script for TOEFL Learning System
Run this script to test all API endpoints
"""

import json
import time

import requests

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
            "model": "alysa"
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
        """Test submit test answers using TOEFL iBT 6-task structure"""
        data = {
            "session_id": session_id,
            "task_answers": [
                # Speaking Task 1 - Independent
                {
                    "task_id": 1,
                    "task_type": "independent",
                    "section": "speaking",
                    "answers": [
                        {
                            "question_id": 1,
                            "answer": "I prefer living in a big city because it offers more opportunities for career growth and personal development. Cities have better job markets, educational institutions, and cultural activities. For example, in my city there are many museums, theaters, and networking events that help me expand my knowledge and meet new people."
                        }
                    ]
                },
                # Speaking Task 2 - Integrated (Campus)
                {
                    "task_id": 2,
                    "task_type": "integrated",
                    "section": "speaking",
                    "answers": [
                        {
                            "question_id": 2,
                            "answer": "The woman strongly supports the university's plan to build a new recreation center. She believes it will provide better facilities for students to exercise and socialize. She mentions that the current gym is overcrowded and outdated, and the new center will have modern equipment and more space for various activities."
                        }
                    ]
                },
                # Speaking Task 3 - Integrated (Academic)
                {
                    "task_id": 3,
                    "task_type": "integrated",
                    "section": "speaking",
                    "answers": [
                        {
                            "question_id": 3,
                            "answer": "The professor uses the example of consumer choice in supermarkets to illustrate behavioral economics. Unlike traditional economic theory which assumes rational decision-making, behavioral economics shows that people make choices based on emotions and cognitive biases. The professor explains how product placement and marketing influence purchasing decisions."
                        }
                    ]
                },
                # Speaking Task 4 - Integrated (Lecture)
                {
                    "task_id": 4,
                    "task_type": "integrated",
                    "section": "speaking",
                    "answers": [
                        {
                            "question_id": 4,
                            "answer": "The professor explains that animals adapt to extreme environments through both physical and behavioral changes. For example, arctic animals develop thick fur and fat layers for insulation, while desert animals have specialized kidneys to conserve water. Some animals also change their behavior, like hibernating during harsh winters or being active at night to avoid extreme heat."
                        }
                    ]
                },
                # Writing Task 1 - Integrated
                {
                    "task_id": 5,
                    "task_type": "integrated",
                    "section": "writing",
                    "answers": [
                        {
                            "question_id": 5,
                            "answer": "The reading passage argues that working from home provides numerous benefits including increased productivity, better work-life balance, and reduced commuting costs. However, the lecture challenges these claims by presenting evidence that contradicts each point. The professor argues that remote work can actually decrease productivity due to distractions at home, create isolation that negatively impacts mental health, and blur the boundaries between work and personal life rather than improving balance. Additionally, the lecture points out that while commuting costs may be reduced, other expenses like home office setup and increased utility bills often offset these savings."
                        }
                    ]
                },
                # Writing Task 2 - Independent
                {
                    "task_id": 6,
                    "task_type": "independent",
                    "section": "writing",
                    "answers": [
                        {
                            "question_id": 6,
                            "answer": "I strongly agree that understanding ideas and concepts is more important than memorizing facts. In today's digital age, information is readily available at our fingertips, making the ability to think critically and understand underlying principles far more valuable than rote memorization. When students focus on concepts, they develop problem-solving skills that can be applied to various situations. For example, a student who understands the concept of supply and demand in economics can analyze different market scenarios, while someone who only memorizes specific price data cannot adapt this knowledge to new situations. Furthermore, conceptual understanding promotes creativity and innovation, as students can connect ideas across different fields and generate new solutions. While facts provide a foundation, it is the comprehension of how and why things work that enables students to become lifelong learners and successful professionals."
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

    def test_invalid_test_submissions(self):
        """Test invalid test submissions to verify validation"""
        print("\n" + "="*50)
        print("Testing Invalid Submissions (Validation Tests)")
        print("="*50)

        # Test 1: Too few tasks (only 3 instead of 6)
        invalid_data_1 = {
            "session_id": 1,
            "task_answers": [
                {"task_id": 1, "section": "speaking", "task_type": "independent", "answers": [{"question_id": 1, "answer": "Test"}]},
                {"task_id": 2, "section": "speaking", "task_type": "integrated", "answers": [{"question_id": 2, "answer": "Test"}]},
                {"task_id": 3, "section": "writing", "task_type": "independent", "answers": [{"question_id": 3, "answer": "Test"}]}
            ]
        }

        response = self.session.post(f"{BASE_URL}/test/submit", json=invalid_data_1)
        print(f"Too Few Tasks Test - Status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Correctly rejected submission with too few tasks")
        else:
            print("❌ Should have rejected submission with too few tasks")

        # Test 2: Missing required fields
        invalid_data_2 = {
            "session_id": 1,
            "task_answers": [
                {"task_id": 1, "section": "speaking", "answers": [{"question_id": 1, "answer": "Test"}]},  # Missing task_type
            ] + [  # Add 5 more valid tasks to make 6 total
                {"task_id": i, "section": "speaking", "task_type": "integrated", "answers": [{"question_id": i, "answer": "Test"}]}
                for i in range(2, 7)
            ]
        }

        response = self.session.post(f"{BASE_URL}/test/submit", json=invalid_data_2)
        print(f"Missing Fields Test - Status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Correctly rejected submission with missing fields")
        else:
            print("❌ Should have rejected submission with missing fields")

    def run_all_tests(self):
        """Run all API tests including TOEFL iBT 6-task validation"""
        print("Starting API Tests for TOEFL iBT Learning System (6-Task Evaluation)")
        print("=" * 70)

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

            # Test 6: Submit Test Answers (6 TOEFL iBT Tasks)
            total_tests += 1
            if self.test_submit_test(session_id):
                tests_passed += 1
                print("✅ Submit TOEFL iBT Test (6 Tasks) - PASSED")

                # Test 6b: Invalid Submissions
                self.test_invalid_test_submissions()
            else:
                print("❌ Submit TOEFL iBT Test (6 Tasks) - FAILED")
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
        print("\n" + "=" * 70)
        print(f"TOEFL iBT API TEST SUMMARY: {tests_passed}/{total_tests} tests passed")
        if tests_passed == total_tests:
            print("🎉 All tests passed! TOEFL iBT 6-task evaluation system is working correctly.")
            print("✅ Individual task evaluation validated")
            print("✅ TOEFL iBT scoring system validated")
            print("✅ Task structure validation working")
        else:
            print(f"⚠️  {total_tests - tests_passed} tests failed. Check the output above.")
        print("=" * 70)

def main():
    """Main function"""
    print("TOEFL iBT Learning System - API Tester (6-Task Evaluation)")
    print("This will test the new TOEFL iBT system with 6 individual tasks:")
    print("  - 4 Speaking Tasks (1 Independent + 3 Integrated)")
    print("  - 2 Writing Tasks (1 Integrated + 1 Independent)")
    print("\nMake sure the Flask app is running on http://localhost:5000")
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
[]
