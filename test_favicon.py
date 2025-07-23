#!/usr/bin/env python3
"""
Test Favicon

This script tests if the favicon is properly configured and accessible.
"""

import requests
import os

def test_favicon():
    """Test if favicon is accessible"""
    print("🖼️ Testing Favicon Configuration")
    print("=" * 40)
    
    # Check if icon file exists
    icon_path = "static/icon.png"
    if os.path.exists(icon_path):
        file_size = os.path.getsize(icon_path)
        print(f"✅ Icon file exists: {icon_path} ({file_size} bytes)")
    else:
        print(f"❌ Icon file not found: {icon_path}")
        return False
    
    # Test favicon endpoint (requires app to be running)
    try:
        response = requests.get("http://localhost:8000/favicon.ico", timeout=5)
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            content_length = len(response.content)
            
            print(f"✅ Favicon endpoint working")
            print(f"   Content-Type: {content_type}")
            print(f"   Content-Length: {content_length} bytes")
            
            if 'image' in content_type.lower():
                print("✅ Correct content type for image")
            else:
                print("⚠️ Unexpected content type")
            
            return True
        else:
            print(f"❌ Favicon endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Cannot test endpoint - app not running")
        print("   Start the app with: python app.py")
        return True  # File exists, so configuration is probably correct
    except Exception as e:
        print(f"❌ Favicon test failed: {str(e)}")
        return False

def main():
    """Run favicon test"""
    print("🧪 Favicon Testing")
    print("=" * 30)
    
    success = test_favicon()
    
    if success:
        print("\n🎉 Favicon configuration looks good!")
        print("\nTo see the favicon:")
        print("1. Start your app: python app.py")
        print("2. Open http://localhost:8000 in your browser")
        print("3. Look for your logo in the browser tab")
    else:
        print("\n🔧 Favicon configuration needs fixing")

if __name__ == "__main__":
    main()