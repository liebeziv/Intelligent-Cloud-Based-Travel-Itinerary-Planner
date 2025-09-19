import requests
import json

def test_recommendation_request():
    url = "http://localhost:8000/api/recommendations/"
    
    
    payload = {
        "user_id": "test_user",
        "preferences": {
            "activity_types": ["natural", "scenic"],
            "budget_range": [100, 400],
            "travel_style": "adventure",
            "group_size": 2,
            "duration": 7
        },
        "current_location": {
            "lat": -41.3,
            "lng": 174.8,
            "address": "Wellington, New Zealand"
        },
        "top_k": 6
    }
    
    try:
        print("Send a referral request...")
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\nResponse data:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if "recommendations" in data:
                print(f"\nNumber of recommendations: {len(data['recommendations'])}")
            else:
                print("\nError: No recommendations field in response")
        else:
            print(f"\nError response:")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("Request timed out")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_recommendation_request()