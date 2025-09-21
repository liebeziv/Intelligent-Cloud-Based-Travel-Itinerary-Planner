#!/usr/bin/env python3


import requests
import json
import time
from datetime import datetime
import uuid

class TravelPlannerTester:
    def __init__(self, base_url="https://d35vyyonooyid7.cloudfront.net"):
        self.base_url = base_url
        self.token = None
        self.test_user_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
      
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def test_health_check(self):
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", True, "API server is running fine")
                    return True
                else:
                    self.log_test("Health Check", False, f"Health status abnormal: {data}")
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Health Check", False, f"Connection failed: {str(e)}")
        return False
    
    def test_api_docs(self):
       
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=10)
            if response.status_code == 200:
                self.log_test("API Documentation", True, "The documentation page can be accessed")
                return True
            else:
                self.log_test("API Documentation", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("API Documentation", False, f"Failed to access documentation: {str(e)}")
        return False
    
    def test_root_endpoint(self):
        
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "version" in data:
                    self.log_test("Root Endpoint", True, f"Version: {data.get('version')}")
                    return True
                else:
                    self.log_test("Root Endpoint", False, "Response format is incorrect")
            else:
                self.log_test("Root Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Request failed: {str(e)}")
        return False
    
    def test_user_registration(self):
       
        try:
            user_data = {
                "email": self.test_user_email,
                "password": "TestPassword123!",
                "name": "Test User"
            }
            
            response = requests.post(
                f"{self.base_url}/api/auth/register", 
                json=user_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("email") == self.test_user_email:
                    self.log_test("User Registration", True, f"User registration successful: {data['id'][:8]}...")
                    return True
                else:
                    self.log_test("User Registration", False, "Response format is incorrect")
            elif response.status_code == 400:
                error_data = response.json()
                if "email exists" in error_data.get("detail", ""):
                    self.log_test("User Registration", True, "Email existence check passed")
                    return True
                else:
                    self.log_test("User Registration", False, f"registration failure: {error_data}")
            else:
                self.log_test("User Registration", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("User Registration", False, f"registration request failed: {str(e)}")
        return False
    
    def test_user_login(self):
     
        try:
            # Try registering a user first
            self.test_user_registration()
            
            login_data = {
                "email": self.test_user_email,
                "password": "TestPassword123!"
            }
            
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "token_type" in data:
                    self.token = data["access_token"]
                    self.log_test("User Login", True, "User login successful, token obtained")
                    return True
                else:
                    self.log_test("User Login", False, "Response is missing token information")
            else:
                self.log_test("User Login", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("User Login", False, f"Login request failed: {str(e)}")
        return False
    
    def test_recommendation_health(self):
        
        try:
            response = requests.get(f"{self.base_url}/api/recommendations/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Recommendation Health", True, "Recommendation system is healthy")
                    return True
                else:
                    self.log_test("Recommendation Health", False, f"Unexpected status: {data}")
            else:
                self.log_test("Recommendation Health", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Recommendation Health", False, f"Request failed: {str(e)}")
        return False
    
    def test_sample_request(self):
        
        try:
            response = requests.get(f"{self.base_url}/api/recommendations/sample-request", timeout=10)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["user_id", "preferences", "current_location", "top_k"]
                if all(field in data for field in required_fields):
                    self.log_test("Sample Request", True, "Sample data format is correct")
                    return True
                else:
                    self.log_test("Sample Request", False, "Sample data is missing required fields")
            else:
                self.log_test("Sample Request", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Sample Request", False, f"Request failed: {str(e)}")
        return False
    
    def test_recommendations(self):
       
        try:
            recommendation_data = {
                "user_id": "test_user_12345",
                "preferences": {
                    "activity_types": ["natural", "scenic", "adventure"],
                    "budget_range": [100, 400],
                    "travel_style": "adventure",
                    "difficulty_preference": "medium",
                    "max_travel_distance": 300,
                    "group_size": 2,
                    "duration": 7
                },
                "current_location": {
                    "lat": -41.3,
                    "lng": 174.8,
                    "address": "Wellington, New Zealand"
                },
                "exclude_visited": ["001"],
                "top_k": 5
            }
            
            response = requests.post(
                f"{self.base_url}/api/recommendations/",
                json=recommendation_data,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if "recommendations" in data and "user_id" in data:
                    recommendations_count = len(data["recommendations"])
                    self.log_test("Recommendations", True, f"{recommendations_count} recommendations retrieved")
                    return True
                else:
                    self.log_test("Recommendations", False, "Response format is incorrect")
            else:
                self.log_test("Recommendations", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Recommendations", False, f"Request failed: {str(e)}")
        return False
    
    def test_protected_endpoints(self):

        if not self.token:
            self.log_test("Protected Endpoints", False, "No valid authentication token")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
 
        try:
            response = requests.get(
                f"{self.base_url}/api/upload-url?filename=test.jpg",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "url" in data and "key" in data:
                    self.log_test("Upload URL", True, "Upload URL retrieved successfully")
                else:
                    self.log_test("Upload URL", False, "Response is missing required fields")
            else:
                self.log_test("Upload URL", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Upload URL", False, f"Request failed: {str(e)}")

     
        try:
            itinerary_data = {
                "title": "Test stroke",
                "items": [
                    {
                        "day": 1,
                        "location": "Wellington",
                        "activities": ["Cable Car", "Te Papa Museum"]
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/api/itineraries",
                json=itinerary_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.log_test("Create Itinerary", True, f"Itinerary created successfully: {data['id'][:8]}...")
                    return True
                else:
                    self.log_test("Create Itinerary", False, "Response is missing itinerary ID")
            else:
                self.log_test("Create Itinerary", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Create Itinerary", False, f"Failed to create itinerary: {str(e)}")

        return False
    
    def test_error_handling(self):
      
        # Test invalid endpoint
        try:
            response = requests.get(f"{self.base_url}/invalid-endpoint", timeout=10)
            if response.status_code == 404:
                self.log_test("404 Error Handling", True, "404 Error Handling works as expected")
            else:
                self.log_test("404 Error Handling", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("404 Error Handling", False, f"Request failed: {str(e)}")

        # Test invalid auth
        try:
            headers = {"Authorization": "Bearer invalid_token"}
            response = requests.get(
                f"{self.base_url}/api/upload-url?filename=test.jpg",
                headers=headers,
                timeout=10
            )
            if response.status_code == 401:
                self.log_test("Invalid Auth Handling", True, "Invalid auth handling works as expected")
            else:
                self.log_test("Invalid Auth Handling", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_test("Invalid Auth Handling", False, f"Request failed: {str(e)}")
    
    def run_all_tests(self):
        
        print("=" * 60)
        print("Automated Testing Begins")
        print("=" * 60)
        
        start_time = time.time()

        print("\n🔍 Basic Functionality Tests:")
        self.test_health_check()
        self.test_api_docs()
        self.test_root_endpoint()
        
        # Authentication System Tests
        print("\n🔐 Authentication System Tests:")
        self.test_user_registration()
        self.test_user_login()
        
        # Recommendation System Tests
        print("\n🎯 Recommendation System Tests:")
        self.test_recommendation_health()
        self.test_sample_request()
        self.test_recommendations()

        # Protected Endpoints Tests
        print("\n🛡️ Protected Endpoints Tests:")
        self.test_protected_endpoints()

        # Error Handling Tests
        print("\n❌ Error Handling Tests:")
        self.test_error_handling()

        # Generate Test Report
        self.generate_report(time.time() - start_time)
    
    def generate_report(self, duration):
        
        print("\n" + "=" * 60)
        print("Test Report")
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

        # Save detailed report to file
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
        
        with open("test_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"\n📊 Detailed report saved to: test_report.json")

if __name__ == "__main__":
    import sys

    # Check server address argument
    base_url = "https://d35vyyonooyid7.cloudfront.net"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print(f"Target server for testing: {base_url}")

    # Run tests
    tester = TravelPlannerTester(base_url)
    tester.run_all_tests()