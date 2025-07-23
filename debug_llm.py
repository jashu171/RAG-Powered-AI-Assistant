#!/usr/bin/env python3
"""
Debug LLM Issues

This script helps diagnose why the LLM is not generating responses.
"""

import os
from dotenv import load_dotenv

def check_api_key():
    """Check if API key is properly configured"""
    print("🔑 Checking API Key Configuration")
    print("-" * 40)
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        print("   Check your .env file")
        return False
    elif api_key == "your_gemini_api_key_here":
        print("❌ GEMINI_API_KEY is still the placeholder value")
        print("   Replace with your actual API key from Google AI Studio")
        return False
    elif len(api_key) < 20:
        print("❌ GEMINI_API_KEY seems too short")
        print(f"   Current length: {len(api_key)} characters")
        return False
    else:
        print(f"✅ GEMINI_API_KEY found (length: {len(api_key)} characters)")
        print(f"   Key starts with: {api_key[:10]}...")
        return True

def test_gemini_connection():
    """Test connection to Gemini API"""
    print("\n🌐 Testing Gemini API Connection")
    print("-" * 40)
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            print("❌ Cannot test - API key not configured")
            return False
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Test simple generation
        print("   Testing simple generation...")
        response = model.generate_content("Say 'Hello, I am working!'")
        
        if response and response.text:
            print(f"✅ Gemini API working! Response: {response.text}")
            return True
        else:
            print("❌ Gemini API returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API test failed: {str(e)}")
        return False

def test_mcp_llm_agent():
    """Test the MCP LLM Agent"""
    print("\n🤖 Testing MCP LLM Agent")
    print("-" * 40)
    
    try:
        from agents.mcp_llm_agent import MCPLLMAgent
        
        # Initialize agent
        llm_agent = MCPLLMAgent()
        print("✅ MCP LLM Agent initialized successfully")
        
        # Test direct response generation
        result = llm_agent.generate_response(
            query="Hello, can you respond?",
            context_chunks=[],
            chunk_metadata=[]
        )
        
        if result.get("status") == "success":
            answer = result.get("answer", "")
            print(f"✅ Direct generation works! Response: {answer[:100]}...")
            return True
        else:
            print(f"❌ Direct generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ MCP LLM Agent test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_workflow():
    """Test the complete MCP workflow"""
    print("\n🔄 Testing Complete MCP Workflow")
    print("-" * 40)
    
    try:
        from agents.mcp_coordinator import MCPCoordinatorAgent
        from utils.mcp import broker, MessageType
        
        # Initialize coordinator
        coordinator = MCPCoordinatorAgent()
        print("✅ Coordinator initialized")
        
        # Test query processing
        query_msg = coordinator.send_message(
            receiver=coordinator.agent_id,
            msg_type=MessageType.QUERY_REQUEST.value,
            payload={
                "query": "Hello, test query",
                "search_k": 3
            }
        )
        
        print(f"✅ Query message sent: {query_msg.trace_id}")
        
        # Check broker stats
        stats = broker.get_stats()
        print(f"✅ Broker stats: {stats['messages_sent']} messages sent")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP workflow test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_app_logs():
    """Check application logs for errors"""
    print("\n📋 Checking Application Logs")
    print("-" * 40)
    
    log_file = "app.log"
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                
            # Get last 10 lines
            recent_lines = lines[-10:] if len(lines) > 10 else lines
            
            print("Recent log entries:")
            for line in recent_lines:
                if "ERROR" in line or "error" in line:
                    print(f"❌ {line.strip()}")
                elif "WARNING" in line or "warning" in line:
                    print(f"⚠️ {line.strip()}")
                else:
                    print(f"ℹ️ {line.strip()}")
                    
        except Exception as e:
            print(f"❌ Could not read log file: {str(e)}")
    else:
        print("ℹ️ No log file found (app.log)")

def main():
    """Run all diagnostic checks"""
    print("🔧 LLM Response Debugging Tool")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    checks = [
        ("API Key Configuration", check_api_key),
        ("Gemini API Connection", test_gemini_connection),
        ("MCP LLM Agent", test_mcp_llm_agent),
        ("MCP Workflow", test_mcp_workflow)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name} check crashed: {str(e)}")
            results[check_name] = False
    
    # Check logs
    check_app_logs()
    
    # Summary
    print("\n📊 Diagnostic Summary")
    print("=" * 50)
    
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {check_name}")
    
    # Recommendations
    print("\n💡 Recommendations")
    print("-" * 30)
    
    if not results.get("API Key Configuration", False):
        print("1. Set your GEMINI_API_KEY in the .env file")
        print("   Get it from: https://makersuite.google.com/app/apikey")
    
    if not results.get("Gemini API Connection", False):
        print("2. Check your internet connection and API key validity")
    
    if not results.get("MCP LLM Agent", False):
        print("3. Check if all dependencies are installed correctly")
        print("   Run: pip install google-generativeai")
    
    if not results.get("MCP Workflow", False):
        print("4. Check if the MCP system is properly initialized")
    
    print("\n🔧 Next Steps:")
    print("1. Fix any failed checks above")
    print("2. Restart the application")
    print("3. Try uploading a document and asking a question")
    print("4. Check the browser's developer console for errors")

if __name__ == "__main__":
    main()