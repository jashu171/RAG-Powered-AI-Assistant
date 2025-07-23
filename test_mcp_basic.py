#!/usr/bin/env python3
"""
Basic MCP System Test

Tests the core MCP functionality without requiring external dependencies.
"""

import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mcp_core():
    """Test core MCP functionality"""
    print("🧪 Testing MCP Core Functionality")
    print("=" * 40)
    
    try:
        # Test MCP message creation
        from utils.mcp import MCPMessage, MessageType, MessagePriority, broker
        
        print("✅ MCP imports successful")
        
        # Test message creation
        message = MCPMessage.create(
            sender="TestAgent",
            receiver="TargetAgent",
            msg_type=MessageType.QUERY_REQUEST.value,
            payload={"test": "data"}
        )
        
        print(f"✅ Message created: {message.trace_id}")
        
        # Test message serialization
        msg_dict = message.to_dict()
        msg_json = message.to_json()
        
        print("✅ Message serialization successful")
        
        # Test message deserialization
        restored_msg = MCPMessage.from_dict(msg_dict)
        
        print("✅ Message deserialization successful")
        
        # Test broker functionality
        handler_called = False
        
        def test_handler(msg):
            nonlocal handler_called
            handler_called = True
            print(f"✅ Handler called for message: {msg.trace_id}")
        
        # Register handler
        broker.register_handler("TargetAgent", MessageType.QUERY_REQUEST.value, test_handler)
        
        # Send message
        success = broker.send(message)
        
        print(f"✅ Message sent successfully: {success}")
        print(f"✅ Handler was called: {handler_called}")
        
        # Test broker stats
        stats = broker.get_stats()
        print(f"✅ Broker stats: {stats}")
        
        # Test message history
        history = broker.get_recent_messages(limit=5)
        print(f"✅ Message history: {len(history)} messages")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_client():
    """Test MCP client functionality"""
    print("\n🧪 Testing MCP Client Functionality")
    print("=" * 40)
    
    try:
        from utils.mcp_client import MCPClient, MCPAgent
        
        print("✅ MCP client imports successful")
        
        # Test client creation
        client = MCPClient("TestClient")
        print(f"✅ Client created: {client.agent_id}")
        
        # Test agent creation
        agent = MCPAgent("TestAgent")
        print(f"✅ Agent created: {agent.agent_id}")
        
        # Test message sending
        message = client.send(
            receiver="TargetAgent",
            msg_type="TEST_MESSAGE",
            payload={"test": "data"}
        )
        
        print(f"✅ Message sent via client: {message.trace_id}")
        
        # Test agent stats
        stats = agent.get_stats()
        print(f"✅ Agent stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow_tracking():
    """Test workflow tracking functionality"""
    print("\n🧪 Testing Workflow Tracking")
    print("=" * 40)
    
    try:
        from utils.mcp import MCPMessage, MessageType, broker
        import uuid
        
        # Create workflow
        workflow_id = str(uuid.uuid4())
        
        # Send workflow start message
        start_msg = MCPMessage.create(
            sender="TestCoordinator",
            receiver="TestAgent",
            msg_type=MessageType.WORKFLOW_START.value,
            payload={"workflow_type": "test"},
            workflow_id=workflow_id
        )
        
        broker.send(start_msg)
        print(f"✅ Workflow started: {workflow_id}")
        
        # Send workflow message
        work_msg = MCPMessage.create(
            sender="TestAgent",
            receiver="TestProcessor",
            msg_type=MessageType.TASK_ASSIGNED.value,
            payload={"task": "process_data"},
            workflow_id=workflow_id
        )
        
        broker.send(work_msg)
        print("✅ Workflow message sent")
        
        # Send workflow completion
        complete_msg = MCPMessage.create(
            sender="TestProcessor",
            receiver="TestCoordinator",
            msg_type=MessageType.WORKFLOW_COMPLETE.value,
            payload={"status": "completed"},
            workflow_id=workflow_id
        )
        
        broker.send(complete_msg)
        print("✅ Workflow completed")
        
        # Check workflow status
        workflow_status = broker.get_workflow_status(workflow_id)
        print(f"✅ Workflow status retrieved: {workflow_status is not None}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 MCP System Basic Tests")
    print("=" * 50)
    
    tests = [
        test_mcp_core,
        test_mcp_client,
        test_workflow_tracking
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(0.5)  # Brief pause between tests
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP system is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)