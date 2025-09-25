#!/usr/bin/env python3
"""
Simple Production Diagnostic for Travel Planner
Quick check of the main issues
"""

import requests
import json
import time

def test_endpoints():
    """Test main endpoints"""
    print("🔍 Testing Production Endpoints...")
    
    base_urls = {
        "CloudFront": "https://d35vyyonooyid7.cloudfront.net",
        "Direct EB": "https://travel-planner-prod.eba-92ixzaqv.us-east-1.elasticbeanstalk.com"
    }
    
    endpoints = [
        ("Health", "/health"),
        ("Root", "/"),
        ("Rec Health", "/api/recommendations/health"),
        ("Sample", "/api/recommendations/sample-request")
    ]
    
    for name, url in base_urls.items():
        print(f"\n  Testing {name}:")
        for endpoint_name, path in endpoints:
            try:
                response = requests.get(f"{url}{path}", timeout=10)
                status = "✅" if response.status_code == 200 else "❌"
                print(f"    {status} {endpoint_name}: HTTP {response.status_code}")
                
                if response.status_code != 200:
                    print(f"      Error: {response.text[:150]}")
                    
            except Exception as e:
                print(f"    ❌ {endpoint_name}: {str(e)}")

def test_recommendation_api():
    """Test the actual recommendation API that's failing"""
    print("\n🎯 Testing Recommendation API...")
    
    test_payload = {
        "user_id": "diagnostic_test",
        "preferences": {
            "activity_types": ["natural", "scenic"],
            "budget_range": [100, 400],
            "travel_style": "adventure",
            "max_travel_distance": 50,
            "group_size": 2,
            "duration": 3
        },
        "current_location": {
            "lat": -41.3,
            "lng": 174.8,
            "address": "Wellington, New Zealand"
        },
        "top_k": 6
    }
    
    base_urls = {
        "CloudFront": "https://d35vyyonooyid7.cloudfront.net",
        "Direct EB": "https://travel-planner-prod.eba-92ixzaqv.us-east-1.elasticbeanstalk.com"
    }
    
    for name, base_url in base_urls.items():
        print(f"\n  Testing {name} Recommendations:")
        try:
            url = f"{base_url}/api/recommendations/"
            
            print(f"    Sending request to: {url}")
            print(f"    Payload: {json.dumps(test_payload, indent=2)}")
            
            response = requests.post(url, json=test_payload, timeout=15)
            
            print(f"    Response Status: {response.status_code}")
            print(f"    Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                rec_count = len(data.get('recommendations', []))
                total_count = data.get('total_count', 0)
                algorithm = data.get('algorithm_used', 'unknown')
                
                print(f"    ✅ Success!")
                print(f"      - Recommendations returned: {rec_count}")
                print(f"      - Total count: {total_count}")
                print(f"      - Algorithm used: {algorithm}")
                
                # Check context for issues
                context = data.get('context', {})
                if context:
                    message = context.get('message', '')
                    if message:
                        print(f"      - Context message: {message}")
                        
                # Show first recommendation if available
                if rec_count > 0:
                    first_rec = data['recommendations'][0]
                    name = first_rec.get('name', 'Unknown')
                    distance = first_rec.get('distance', 'N/A')
                    score = first_rec.get('confidence_score', 0)
                    print(f"      - First recommendation: {name} (Distance: {distance}km, Score: {score:.3f})")
                else:
                    print(f"      ❌ No recommendations returned!")
                    print(f"      Full response: {json.dumps(data, indent=2)}")
                    
            else:
                print(f"    ❌ Request failed!")
                print(f"    Response text: {response.text}")
                
        except Exception as e:
            print(f"    ❌ Exception occurred: {str(e)}")

def test_itinerary_planning():
    """Test itinerary planning endpoint"""
    print("\n🗓️ Testing Itinerary Planning...")
    
    test_payload = {
        "user_id": "diagnostic_test",
        "preferences": {
            "activity_types": ["natural", "scenic"],
            "budget_range": [100, 400],
            "travel_style": "adventure",
            "max_travel_distance": 200,  # Increased distance
            "group_size": 2,
            "duration": 3
        },
        "current_location": {
            "lat": -41.3,
            "lng": 174.8,
            "address": "Wellington, New Zealand"
        },
        "top_k": 8,
        "save": False
    }
    
    try:
        url = "https://d35vyyonooyid7.cloudfront.net/api/itineraries/plan"
        response = requests.post(url, json=test_payload, timeout=20)
        
        print(f"  Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            days = len(data.get('days', []))
            recs = len(data.get('recommendations', []))
            
            print(f"  ✅ Itinerary planning succeeded!")
            print(f"    - Days generated: {days}")
            print(f"    - Recommendations: {recs}")
            
            if days == 0:
                print(f"    ❌ No itinerary was generated!")
                context = data.get('context')
                if isinstance(context, str):
                    print(f"    Context: {context}")
                elif isinstance(context, dict):
                    message = context.get('message', 'No message')
                    print(f"    Context message: {message}")
                    
                print(f"    Full response: {json.dumps(data, indent=2)}")
            else:
                summary = data.get('summary', {})
                print(f"    Summary: {summary}")
                
        else:
            print(f"  ❌ Itinerary planning failed!")
            print(f"  Response: {response.text}")
            
    except Exception as e:
        print(f"  ❌ Exception in itinerary planning: {str(e)}")

def check_attractions_data():
    """Check if attractions data is available"""
    print("\n📊 Checking Attractions Data...")
    
    try:
        url = "https://d35vyyonooyid7.cloudfront.net/api/attractions"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"  ✅ Attractions data available: {len(data)} attractions")
                
                # Group by region
                regions = {}
                for attraction in data:
                    region = attraction.get('region', 'Unknown')
                    regions[region] = regions.get(region, 0) + 1
                    
                print(f"  Attractions by region:")
                for region, count in regions.items():
                    print(f"    {region}: {count}")
                    
            else:
                print(f"  ⚠️ Unexpected data format: {type(data)}")
                
        else:
            print(f"  ❌ Attractions endpoint failed: HTTP {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"  ❌ Failed to check attractions data: {str(e)}")

def main():
    """Run all diagnostic tests"""
    print("=" * 60)
    print("TRAVEL PLANNER PRODUCTION DIAGNOSTIC")
    print("=" * 60)
    print("This will test the specific issue you're experiencing")
    print()
    
    # Run tests in order
    test_endpoints()
    check_attractions_data() 
    test_recommendation_api()
    test_itinerary_planning()
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)
    print("💡 Key things to check:")
    print("1. Are all endpoints returning HTTP 200?")
    print("2. Is attractions data loaded properly?")
    print("3. Does the recommendation API return any results?")
    print("4. What's the exact error message from itinerary planning?")

if __name__ == "__main__":
    main()