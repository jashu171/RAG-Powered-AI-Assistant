#!/usr/bin/env python3
"""
Test API Endpoints

This script tests the Flask API endpoints to see if they're working.
"""

import requests
import json
import time

def test_health_endpoint():
    """Test the health endpoint"""
    print("🏥 Testing Health Endpoint")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working")
            print(f"   Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - is the app running?")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

def test_query_endpoint():
    """Test the query endpoint"""
    print("\n❓ Testing Query Endpoint")
    print("-" * 30)
    
    try:
        payload = {
            "query": "Hello, this is a test query",
            "search_k": 3
        }
        
        response = requests.post(
            "http://localhost:8000/query",
            json=payload,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Query endpoint responded")
            print(f"   Keys in response: {list(data.keys())}")
            
            if "answer" in data:
                answer = data["answer"]
                print(f"   Answer: {answer[:100]}...")
                return True
            else:
                print("   ⚠️ No 'answer' field in response")
                print(f"   Full response: {json.dumps(data, indent=2)}")
                return False
        else:
            print(f"❌ Query endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - is the app running?")
        return False
    except Exception as e:
        print(f"❌ Query test failed: {str(e)}")
        return False

def test_stats_endpoint():
    """Test the stats endpoint"""
    print("\n📊 Testing Stats Endpoint")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8000/stats", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Stats endpoint working")
            
            if "pipeline_stats" in data:
                pipeline_stats = data["pipeline_stats"]
                print(f"   Pipeline components: {list(pipeline_stats.keys())}")
            
            if "broker_stats" in data:
                broker_stats = data["broker_stats"]
                messages_sent = broker_stats.get("messages_sent", 0)
                print(f"   Messages sent: {messages_sent}")
            
            return True
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Stats test failed: {str(e)}")
        return False

def main():
    """Run all API tests"""
    print("🧪 API Endpoint Testing")
    print("=" * 40)
    
    print("Make sure your app is running on http://localhost:8000")
    print("If not, run: python app.py")
    print()
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Query Endpoint", test_query_endpoint),
        ("Stats Endpoint", test_stats_endpoint)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        results[test_name] = test_func()
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n📊 Test Results")
    print("=" * 30)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
    
    if not any(results.values()):
        print("\n🚨 All tests failed - check if the app is running!")
        print("Run: python app.py")
    elif not results.get("Query Endpoint", False):
        print("\n🔧 Query endpoint issues detected")
        print("This is likely why you're not getting LLM responses")

if __name__ == "__main__":
    main()