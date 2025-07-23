#!/usr/bin/env python3
"""
Test LLM Direct Response

This script tests the LLM agent directly to ensure it's working.
"""

import os
from dotenv import load_dotenv

def test_llm_direct():
    """Test LLM agent directly"""
    print("🤖 Testing LLM Agent Directly")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("❌ GEMINI_API_KEY not configured properly")
        print("Please set your API key in the .env file")
        return False
    
    try:
        # Test direct Gemini API
        print("1. Testing direct Gemini API...")
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        response = model.generate_content("Hello! Can you respond with 'Yes, I am working!'?")
        
        if response and response.text:
            print(f"✅ Direct API works: {response.text}")
        else:
            print("❌ Direct API failed - no response")
            return False
        
        # Test MCP LLM Agent
        print("\n2. Testing MCP LLM Agent...")
        from agents.mcp_llm_agent import MCPLLMAgent
        
        llm_agent = MCPLLMAgent()
        print("✅ LLM Agent initialized")
        
        # Test with no context (general response)
        result = llm_agent.generate_response(
            query="Hello! Please respond with 'LLM Agent is working!'",
            context_chunks=[],
            chunk_metadata=[]
        )
        
        if result.get("status") == "success":
            answer = result.get("answer", "")
            print(f"✅ LLM Agent works: {answer[:100]}...")
            return True
        else:
            print(f"❌ LLM Agent failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_pipeline():
    """Test the complete pipeline"""
    print("\n🔄 Testing Complete Pipeline")
    print("=" * 40)
    
    try:
        from agents.mcp_coordinator import MCPCoordinatorAgent
        
        coordinator = MCPCoordinatorAgent()
        print("✅ Coordinator initialized")
        
        # Test retrieval (should work even with no documents)
        retrieval_result = coordinator.retrieval_agent.retrieve_context(
            query="Hello test query",
            k=3
        )
        
        print(f"✅ Retrieval result: {retrieval_result.get('status', 'unknown')}")
        
        # Test LLM generation
        llm_result = coordinator.llm_agent.generate_response(
            query="Hello! Please say 'Pipeline is working!'",
            context_chunks=[],
            chunk_metadata=[]
        )
        
        if llm_result.get("status") == "success":
            answer = llm_result.get("answer", "")
            print(f"✅ Complete pipeline works: {answer[:100]}...")
            return True
        else:
            print(f"❌ Pipeline failed: {llm_result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Pipeline test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 LLM Direct Testing")
    print("=" * 50)
    
    tests = [
        ("Direct LLM", test_llm_direct),
        ("Complete Pipeline", test_complete_pipeline)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Summary
    print("\n📊 Test Results")
    print("=" * 30)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
    
    if all(results.values()):
        print("\n🎉 All tests passed! LLM should be working now.")
        print("Restart your app and try asking a question.")
    else:
        print("\n🔧 Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()