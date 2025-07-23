#!/usr/bin/env python3
"""
Test Query Flow

This script tests the complete query processing flow.
"""

import time
from agents.mcp_coordinator import MCPCoordinatorAgent
from utils.mcp import broker, MessageType

def test_query_flow():
    """Test the complete query flow"""
    print("🔄 Testing Query Processing Flow")
    print("=" * 40)
    
    # Set up message logging
    messages_log = []
    
    original_send = broker.send
    def logged_send(message):
        messages_log.append({
            "sender": message.sender,
            "receiver": message.receiver,
            "type": message.type,
            "trace_id": message.trace_id,
            "payload_keys": list(message.payload.keys())
        })
        print(f"📨 {message.sender} → {message.receiver}: {message.type}")
        return original_send(message)
    
    broker.send = logged_send
    
    try:
        # Initialize coordinator
        coordinator = MCPCoordinatorAgent()
        print("✅ Coordinator initialized")
        
        # Send a test query
        print("\n📤 Sending test query...")
        query_msg = coordinator.send_message(
            receiver=coordinator.agent_id,
            msg_type=MessageType.QUERY_REQUEST.value,
            payload={
                "query": "Hello, this is a test query",
                "search_k": 3
            }
        )
        
        print(f"Query sent with trace ID: {query_msg.trace_id}")
        
        # Wait a bit for processing
        time.sleep(2)
        
        # Show message flow
        print(f"\n📋 Message Flow ({len(messages_log)} messages):")
        for i, msg in enumerate(messages_log, 1):
            print(f"  {i}. {msg['sender']} → {msg['receiver']}: {msg['type']}")
            print(f"     Trace: {msg['trace_id'][:8]}...")
            print(f"     Payload keys: {msg['payload_keys']}")
        
        # Check if we got a response
        response_messages = [m for m in messages_log if m['type'] == 'RESPONSE_GENERATED']
        if response_messages:
            print(f"\n✅ Found {len(response_messages)} response messages!")
        else:
            print(f"\n❌ No response messages found")
            
            # Check for errors
            error_messages = [m for m in messages_log if m['type'] == 'ERROR']
            if error_messages:
                print(f"⚠️ Found {len(error_messages)} error messages")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_query_flow()