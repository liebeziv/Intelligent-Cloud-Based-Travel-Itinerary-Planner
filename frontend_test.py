#!/usr/bin/env python3
"""
Frontend Functionality Test Script
Tests Vue.js frontend integration with FastAPI backend
"""

import requests
import time
import json
from datetime import datetime
import subprocess
import sys
import os

class FrontendTester:
    def __init__(self, backend_url="http://localhost:8000", frontend_url="http://localhost:3000"):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Record test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} {test_name}: {message}")
    
    def check_backend_status(self):
        """Check if backend service is running"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_test("Backend Health Check", True, "Backend API service is running")
                return True
            else:
                self.log_test("Backend Health Check", False, f"Backend returned status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Cannot connect to backend: {str(e)}")
            return False
    
    def check_frontend_status(self):
        """Check if frontend service is running"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.log_test("Frontend Accessibility", True, "Frontend application is accessible")
                return True
            else:
                self.log_test("Frontend Accessibility", False, f"Frontend returned status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Accessibility", False, f"Cannot connect to frontend: {str(e)}")
            return False
    
    def test_cors_configuration(self):
        """Test CORS configuration"""
        try:
            headers = {
                'Origin': self.frontend_url,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            response = requests.options(f"{self.backend_url}/api/auth/register", headers=headers, timeout=5)
            
            if response.status_code in [200, 204]:
                cors_headers = response.headers.get('Access-Control-Allow-Origin', '')
                if cors_headers == '*' or self.frontend_url in cors_headers:
                    self.log_test("CORS Configuration", True, "CORS configuration is correct")
                    return True
                else:
                    self.log_test("CORS Configuration", False, f"CORS configuration incorrect: {cors_headers}")
            else:
                self.log_test("CORS Configuration", False, f"OPTIONS request failed: {response.status_code}")
        except Exception as e:
            self.log_test("CORS Configuration", False, f"CORS test failed: {str(e)}")
        return False
    
    def test_api_endpoints_from_frontend(self):
        """Simulate frontend API calls test"""
        headers = {
            'Content-Type': 'application/json',
            'Origin': self.frontend_url
        }
        
        # Test user registration
        try:
            user_data = {
                "email": f"frontend_test_{int(time.time())}@example.com",
                "password": "FrontendTest123!",
                "name": "Frontend Test User"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/auth/register",
                json=user_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "email" in data:
                    self.log_test("Frontend Registration", True, "User registration API works properly")
                    return user_data
                else:
                    self.log_test("Frontend Registration", False, "Registration response format error")
            else:
                self.log_test("Frontend Registration", False, f"Registration failed: {response.status_code}")
        except Exception as e:
            self.log_test("Frontend Registration", False, f"Registration request failed: {str(e)}")
        
        return None
    
    def test_authentication_flow(self, user_data):
        """Test authentication flow"""
        if not user_data:
            self.log_test("Authentication Flow", False, "No valid user data")
            return None
            
        headers = {
            'Content-Type': 'application/json',
            'Origin': self.frontend_url
        }
        
        try:
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            
            response = requests.post(
                f"{self.backend_url}/api/auth/login",
                json=login_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.log_test("Authentication Flow", True, "User login API works properly")
                    return data["access_token"]
                else:
                    self.log_test("Authentication Flow", False, "Login response missing token")
            else:
                self.log_test("Authentication Flow", False, f"Login failed: {response.status_code}")
        except Exception as e:
            self.log_test("Authentication Flow", False, f"Login request failed: {str(e)}")
        
        return None
    
    def test_recommendation_system_integration(self):
        """Test recommendation system integration"""
        headers = {
            'Content-Type': 'application/json',
            'Origin': self.frontend_url
        }
        
        try:
            recommendation_data = {
                "user_id": "frontend_test_user",
                "preferences": {
                    "activity_types": ["natural", "scenic"],
                    "budget_range": [100, 400],
                    "travel_style": "adventure",
                    "group_size": 2,
                    "duration": 5
                },
                "current_location": {
                    "lat": -41.3,
                    "lng": 174.8,
                    "address": "Wellington, New Zealand"
                },
                "top_k": 5
            }
            
            response = requests.post(
                f"{self.backend_url}/api/recommendations/",
                json=recommendation_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if "recommendations" in data and "user_id" in data:
                    recommendation_count = len(data["recommendations"])
                    self.log_test("Recommendation Integration", True, f"Recommendation system returned {recommendation_count} results")
                    return True
                else:
                    self.log_test("Recommendation Integration", False, "Recommendation response format error")
            else:
                self.log_test("Recommendation Integration", False, f"Recommendation request failed: {response.status_code}")
        except Exception as e:
            self.log_test("Recommendation Integration", False, f"Recommendation request failed: {str(e)}")
        
        return False
    
    def test_protected_endpoints(self, token):
        """Test authenticated endpoints"""
        if not token:
            self.log_test("Protected Endpoints", False, "No valid authentication token")
            return False
            
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
            'Origin': self.frontend_url
        }
        
        try:
            # Test itinerary creation
            itinerary_data = {
                "title": "Frontend Test Itinerary",
                "items": ["Wellington Cable Car", "Te Papa Museum"]
            }
            
            response = requests.post(
                f"{self.backend_url}/api/itineraries",
                json=itinerary_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.log_test("Protected Endpoints", True, "Authenticated API calls successful")
                    return True
                else:
                    self.log_test("Protected Endpoints", False, "Itinerary creation response format error")
            else:
                self.log_test("Protected Endpoints", False, f"Itinerary creation failed: {response.status_code}")
        except Exception as e:
            self.log_test("Protected Endpoints", False, f"Itinerary creation request failed: {str(e)}")
        
        return False
    
    def check_frontend_features(self):
        """Check frontend-specific features"""
        features_to_check = [
            ("/docs", "API Documentation Accessibility"),
            ("/api/recommendations/sample-request", "Sample Request Data"),
            ("/api/recommendations/health", "Recommendation System Health Check")
        ]
        
        for endpoint, description in features_to_check:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.log_test(f"Frontend Feature: {description}", True, "Endpoint accessible")
                else:
                    self.log_test(f"Frontend Feature: {description}", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test(f"Frontend Feature: {description}", False, f"Request failed: {str(e)}")
    
    def check_technology_stack(self):
        """Check technology stack components"""
        print("\n📋 Checking Technology Stack Components:")
        
        # Check Node.js and npm
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.log_test("Node.js Installation", True, f"Version: {result.stdout.strip()}")
            else:
                self.log_test("Node.js Installation", False, "Node.js not installed or configured incorrectly")
        except Exception as e:
            self.log_test("Node.js Installation", False, f"Cannot check Node.js: {str(e)}")
        
        # Check Vue.js project files
        vue_files = ['package.json', 'vite.config.js', 'index.html']
        for file in vue_files:
            if os.path.exists(file):
                self.log_test(f"Vue.js Project File: {file}", True, "File exists")
            else:
                self.log_test(f"Vue.js Project File: {file}", False, "File does not exist")
    
    def run_comprehensive_test(self):
        """Run comprehensive tests"""
        print("=" * 60)
        print("Frontend Functionality Comprehensive Test Started")
        print("=" * 60)
        
        start_time = time.time()
        
        # Basic service checks
        print("\n🔍 Basic Service Checks:")
        backend_ok = self.check_backend_status()
        frontend_ok = self.check_frontend_status()
        
        if not backend_ok:
            print("\n❌ Backend service not running, cannot continue testing")
            return
        
        # CORS configuration test
        print("\n🌐 Cross-Origin Configuration Test:")
        self.test_cors_configuration()
        
        # API integration tests
        print("\n🔗 API Integration Tests:")
        user_data = self.test_api_endpoints_from_frontend()
        token = self.test_authentication_flow(user_data)
        self.test_recommendation_system_integration()
        self.test_protected_endpoints(token)
        
        # Frontend feature checks
        print("\n🎨 Frontend Feature Checks:")
        self.check_frontend_features()
        
        # Technology stack check
        self.check_technology_stack()
        
        # Generate report
        self.generate_frontend_report(time.time() - start_time)
    
    def generate_frontend_report(self, duration):
        """Generate frontend test report"""
        print("\n" + "=" * 60)
        print("Frontend Test Report")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print(f"\n✅ Passed Tests ({passed_tests}):")
        for result in self.test_results:
            if result["success"]:
                print(f"  - {result['test']}: {result['message']}")
        
        # Save detailed report
        report_data = {
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": passed_tests/total_tests*100,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            },
            "tests": self.test_results
        }
        
        with open("frontend_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Detailed report saved to: frontend_test_report.json")
        
        # Provide next step recommendations
        print(f"\n💡 Next Step Recommendations:")
        if failed_tests == 0:
            print("  - All tests passed, ready for user acceptance testing")
            print("  - Consider deploying to AWS production environment")
            print("  - Conduct performance and security testing")
        else:
            print("  - Fix failed test items")
            print("  - Ensure frontend service is running properly")
            print("  - Check network connections and port configurations")

if __name__ == "__main__":
    print("Frontend Functionality Test Script")
    print("Ensure backend service is running at http://localhost:8000")
    print("Ensure frontend service is running at http://localhost:3000")
    print("-" * 50)
    
    tester = FrontendTester()
    tester.run_comprehensive_test()