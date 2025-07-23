#!/usr/bin/env python3
"""
Test MCP Imports

This script tests that all MCP imports are working correctly without requiring
external dependencies like document processing libraries.
"""

import sys
import os

def test_mcp_imports():
    """Test core MCP functionality imports"""
    print("🧪 Testing MCP Imports")
    print("=" * 30)
    
    try:
        # Test core MCP imports
        from utils.mcp import MCPMessage, MessageType, MessagePriority, broker
        print("✅ Core MCP imports successful")
        
        # Test MCP client imports
        from utils.mcp_client import MCPClient, MCPAgent
        print("✅ MCP client imports successful")
        
        # Test agents init imports
        from agents import MCPMessage as AgentMCPMessage, MessageType as AgentMessageType, broker as agent_broker
        print("✅ Agents __init__.py imports successful")
        
        # Test message creation
        message = MCPMessage.create(
            sender="TestSender",
            receiver="TestReceiver",
            msg_type=MessageType.QUERY_REQUEST.value,
            payload={"test": "data"}
        )
        print("✅ Message creation successful")
        
        # Test broker functionality
        handler_called = False
        
        def test_handler(msg):
            nonlocal handler_called
            handler_called = True
        
        broker.register_handler("TestReceiver", MessageType.QUERY_REQUEST.value, test_handler)
        broker.send(message)
        
        if handler_called:
            print("✅ Broker message handling successful")
        else:
            print("❌ Broker message handling failed")
        
        # Test broker stats
        stats = broker.get_stats()
        print(f"✅ Broker stats: {stats['messages_sent']} messages sent")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_config_imports():
    """Test configuration imports"""
    print("\n🧪 Testing Config Imports")
    print("=" * 30)
    
    try:
        from config import config
        print("✅ Config import successful")
        
        # Test config access
        chunk_size = config.agent.chunk_size
        print(f"✅ Config access successful: chunk_size = {chunk_size}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {str(e)}")
        return False

def main():
    """Run all import tests"""
    print("🚀 MCP Import Tests")
    print("=" * 40)
    
    tests = [
        test_mcp_imports,
        test_config_imports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All import tests passed!")
        print("\nNote: To run the full system, install dependencies with:")
        print("pip install -r requirements.txt")
        return True
    else:
        print("❌ Some import tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)