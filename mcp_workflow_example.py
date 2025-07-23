#!/usr/bin/env python3
"""
Complete MCP Workflow Example

This script demonstrates the complete Model Context Protocol (MCP) workflow
as described in the requirements, showing the exact message passing pattern.
"""

import time
import logging
import json
from typing import Dict, Any
from agents.mcp_coordinator import MCPCoordinatorAgent
from utils.mcp import broker, MessageType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class MCPWorkflowDemo:
    """Demonstration of the complete MCP workflow"""
    
    def __init__(self):
        self.coordinator = MCPCoordinatorAgent()
        self.message_log = []
        self.setup_message_logging()
    
    def setup_message_logging(self):
        """Set up message logging to track the complete workflow"""
        # Register a global message handler to log all messages
        original_send = broker.send
        
        def logged_send(message):
            self.message_log.append({
                "timestamp": time.time(),
                "sender": message.sender,
                "receiver": message.receiver,
                "type": message.type,
                "trace_id": message.trace_id,
                "workflow_id": message.workflow_id,
                "payload_summary": self._summarize_payload(message.payload)
            })
            return original_send(message)
        
        broker.send = logged_send
    
    def _summarize_payload(self, payload: Dict[str, Any]) -> str:
        """Create a summary of the payload for logging"""
        if "query" in payload:
            return f"query: '{payload['query'][:50]}...'"
        elif "file_path" in payload:
            return f"file_path: '{payload['file_path']}'"
        elif "chunks" in payload:
            return f"chunks: {len(payload['chunks'])} items"
        elif "top_chunks" in payload:
            return f"top_chunks: {len(payload['top_chunks'])} items"
        elif "answer" in payload:
            return f"answer: '{payload['answer'][:50]}...'"
        else:
            return f"keys: {list(payload.keys())}"
    
    def run_complete_workflow(self):
        """
        Run the complete workflow as described in the requirements:
        
        User uploads: sales_review.pdf, metrics.csv
        User: "What KPIs were tracked in Q1?"
        ➡️ UI forwards to CoordinatorAgent
        ➡️ Coordinator triggers:
        🔸 IngestionAgent → parses documents
        🔸 RetrievalAgent → finds relevant chunks
        🔸 LLMResponseAgent → formats prompt & calls LLM
        ➡️ Chatbot shows answer + source chunks
        """
        print("🚀 Complete MCP Workflow Demonstration")
        print("=" * 60)
        
        # Step 1: Document Upload and Processing
        print("\n📄 Step 1: Document Upload and Processing")
        print("-" * 40)
        
        # Simulate uploading sales_review.pdf and metrics.csv
        test_files = [
            "uploads/sales_review.pdf",
            "uploads/metrics.csv"
        ]
        
        # Create test files if they don't exist
        self._create_test_files(test_files)
        
        # Process each document
        for file_path in test_files:
            print(f"\n📤 Uploading: {file_path}")
            
            # Send ingestion request to coordinator
            ingestion_msg = self.coordinator.send_message(
                receiver=self.coordinator.agent_id,
                msg_type=MessageType.INGESTION_REQUEST.value,
                payload={
                    "file_path": file_path,
                    "chunk_size": 1000,
                    "chunk_overlap": 200
                }
            )
            
            print(f"   📋 Workflow started: {ingestion_msg.workflow_id}")
            print(f"   🔍 Trace ID: {ingestion_msg.trace_id}")
            
            # Wait a bit for processing
            time.sleep(1)
        
        # Step 2: Query Processing
        print("\n❓ Step 2: Query Processing")
        print("-" * 40)
        
        query = "What KPIs were tracked in Q1?"
        print(f"\n🤔 User query: '{query}'")
        
        # Send query request to coordinator
        query_msg = self.coordinator.send_message(
            receiver=self.coordinator.agent_id,
            msg_type=MessageType.QUERY_REQUEST.value,
            payload={
                "query": query,
                "search_k": 5
            }
        )
        
        print(f"   📋 Workflow started: {query_msg.workflow_id}")
        print(f"   🔍 Trace ID: {query_msg.trace_id}")
        
        # Wait for processing
        time.sleep(2)
        
        # Step 3: Show Message Flow
        print("\n📨 Step 3: Complete Message Flow")
        print("-" * 40)
        
        self._show_message_flow()
        
        # Step 4: Show Example Messages
        print("\n📋 Step 4: Example MCP Messages")
        print("-" * 40)
        
        self._show_example_messages()
        
        # Step 5: Show System Stats
        print("\n📊 Step 5: System Statistics")
        print("-" * 40)
        
        self._show_system_stats()
    
    def _create_test_files(self, file_paths):
        """Create test files for demonstration"""
        import os
        
        # Ensure uploads directory exists
        os.makedirs("uploads", exist_ok=True)
        
        # Create sales_review.pdf content (as text for demo)
        sales_content = """
        Q1 Sales Review Report
        
        Key Performance Indicators (KPIs) Tracked:
        1. Revenue Growth: 15% increase compared to Q4
        2. Customer Acquisition: 250 new customers
        3. Customer Retention Rate: 92%
        4. Average Deal Size: $12,500
        5. Sales Cycle Length: 45 days average
        6. Lead Conversion Rate: 18%
        7. Market Share: 8.5% in target segment
        
        Regional Performance:
        - North America: $2.1M revenue
        - Europe: $1.8M revenue  
        - Asia Pacific: $1.2M revenue
        
        Top Performing Products:
        - Product A: 35% of total revenue
        - Product B: 28% of total revenue
        - Product C: 22% of total revenue
        """
        
        # Create metrics.csv content
        metrics_content = """KPI,Q1_Target,Q1_Actual,Q1_Performance
Revenue_Growth,12%,15%,125%
Customer_Acquisition,200,250,125%
Retention_Rate,90%,92%,102%
Average_Deal_Size,$10000,$12500,125%
Sales_Cycle_Days,50,45,110%
Lead_Conversion,15%,18%,120%
Market_Share,8%,8.5%,106%
Customer_Satisfaction,4.2,4.5,107%
"""
        
        # Write test files
        for file_path in file_paths:
            if "sales_review" in file_path:
                with open(file_path, 'w') as f:
                    f.write(sales_content)
            elif "metrics" in file_path:
                with open(file_path, 'w') as f:
                    f.write(metrics_content)
        
        print(f"✅ Created {len(file_paths)} test files")
    
    def _show_message_flow(self):
        """Show the complete message flow"""
        print("\n🔄 Message Flow Sequence:")
        
        for i, msg in enumerate(self.message_log[-20:], 1):  # Show last 20 messages
            timestamp = time.strftime("%H:%M:%S", time.localtime(msg["timestamp"]))
            print(f"   {i:2d}. [{timestamp}] {msg['sender']} → {msg['receiver']}")
            print(f"       Type: {msg['type']}")
            print(f"       Trace: {msg['trace_id'][:8]}...")
            if msg['workflow_id']:
                print(f"       Workflow: {msg['workflow_id'][:8]}...")
            print(f"       Payload: {msg['payload_summary']}")
            print()
    
    def _show_example_messages(self):
        """Show example MCP messages in the required format"""
        
        # Example 1: Retrieval Result (as specified in requirements)
        example_retrieval = {
            "type": "RETRIEVAL_RESULT",
            "sender": "RetrievalAgent",
            "receiver": "LLMResponseAgent",
            "trace_id": "rag-457",
            "payload": {
                "retrieved_context": [
                    "slide 3: revenue up 15% in Q1",
                    "doc: Q1 summary shows KPIs: Revenue Growth 15%, Customer Acquisition 250 new customers"
                ],
                "query": "What KPIs were tracked in Q1?"
            }
        }
        
        # Example 2: Context Response
        example_context = {
            "sender": "RetrievalAgent",
            "receiver": "LLMResponseAgent",
            "type": "CONTEXT_RESPONSE",
            "trace_id": "abc-123",
            "payload": {
                "top_chunks": [
                    "Key Performance Indicators (KPIs) Tracked: 1. Revenue Growth: 15% increase",
                    "Customer Acquisition: 250 new customers, Customer Retention Rate: 92%"
                ],
                "query": "What are the KPIs?"
            }
        }
        
        # Example 3: Document Processed
        example_document = {
            "sender": "IngestionAgent",
            "receiver": "RetrievalAgent",
            "type": "DOCUMENT_PROCESSED",
            "trace_id": "doc-789",
            "payload": {
                "chunks": ["Q1 Sales Review Report...", "Key Performance Indicators..."],
                "file_path": "uploads/sales_review.pdf",
                "chunk_count": 15
            }
        }
        
        examples = [
            ("Retrieval Result (as per requirements)", example_retrieval),
            ("Context Response", example_context),
            ("Document Processed", example_document)
        ]
        
        for title, example in examples:
            print(f"\n📝 {title}:")
            print(json.dumps(example, indent=2))
    
    def _show_system_stats(self):
        """Show system statistics"""
        try:
            # Get pipeline stats
            pipeline_stats = self.coordinator.get_pipeline_stats()
            
            print("\n📈 Pipeline Statistics:")
            for component, stats in pipeline_stats.items():
                print(f"\n   {component.title()}:")
                for key, value in stats.items():
                    if isinstance(value, (int, float)) and key != "timestamp":
                        print(f"     - {key}: {value}")
            
            # Get broker stats
            broker_stats = broker.get_stats()
            print(f"\n🔄 Broker Statistics:")
            for key, value in broker_stats.items():
                print(f"   - {key}: {value}")
            
            # Get active workflows
            active_workflows = self.coordinator.get_active_workflows()
            print(f"\n⚡ Active Workflows: {len(active_workflows)}")
            
            # Get registered agents
            agents = broker.get_registered_agents()
            print(f"\n🤖 Registered Agents: {len(agents)}")
            for agent in agents:
                print(f"   - {agent}")
            
        except Exception as e:
            print(f"❌ Error getting stats: {str(e)}")


def main():
    """Run the complete MCP workflow demonstration"""
    try:
        demo = MCPWorkflowDemo()
        demo.run_complete_workflow()
        
        print("\n🎉 MCP Workflow Demonstration Complete!")
        print("\nKey Features Demonstrated:")
        print("✅ Structured MCP message passing")
        print("✅ Multi-agent coordination")
        print("✅ Workflow tracking with trace IDs")
        print("✅ Document processing pipeline")
        print("✅ Query processing with RAG")
        print("✅ Error handling and recovery")
        print("✅ System monitoring and stats")
        
        print("\nNext Steps:")
        print("1. Run 'python app.py' to start the web server")
        print("2. Upload documents via the web interface")
        print("3. Ask questions about your documents")
        print("4. Monitor workflows at /workflows endpoint")
        print("5. Check system health at /health endpoint")
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}", exc_info=True)
        print(f"❌ Demo failed: {str(e)}")


if __name__ == "__main__":
    main()