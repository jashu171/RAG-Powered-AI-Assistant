"""
Model Context Protocol (MCP) Implementation

This module provides a standardized way for agents to communicate using structured message objects.
It implements the Model Context Protocol (MCP) for inter-agent communication in the RAG system.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
import uuid
import time
import logging
import json
from enum import Enum

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Standard message types for MCP communication"""
    # Document processing
    DOCUMENT_PROCESSED = "DOCUMENT_PROCESSED"
    DOCUMENTS_INDEXED = "DOCUMENTS_INDEXED"
    INGESTION_REQUEST = "INGESTION_REQUEST"
    
    # Query processing
    QUERY_REQUEST = "QUERY_REQUEST"
    CONTEXT_RESPONSE = "CONTEXT_RESPONSE"
    RETRIEVAL_RESULT = "RETRIEVAL_RESULT"
    RESPONSE_GENERATED = "RESPONSE_GENERATED"
    
    # System messages
    ERROR = "ERROR"
    HEALTH_CHECK = "HEALTH_CHECK"
    AGENT_STATUS = "AGENT_STATUS"
    SYSTEM_STATUS = "SYSTEM_STATUS"
    
    # Workflow control
    WORKFLOW_START = "WORKFLOW_START"
    WORKFLOW_COMPLETE = "WORKFLOW_COMPLETE"
    TASK_ASSIGNED = "TASK_ASSIGNED"
    TASK_COMPLETED = "TASK_COMPLETED"

class MessagePriority(Enum):
    """Priority levels for MCP messages"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class MCPMessage:
    """
    Standard MCP message format for inter-agent communication
    
    Example:
    {
        "sender": "RetrievalAgent",
        "receiver": "LLMResponseAgent", 
        "type": "CONTEXT_RESPONSE",
        "trace_id": "abc-123",
        "payload": {
            "top_chunks": ["...", "..."],
            "query": "What are the KPIs?"
        }
    }
    
    Attributes:
        sender: Source agent identifier
        receiver: Target agent identifier
        type: Message type (from MessageType enum)
        trace_id: Unique identifier for message tracing
        payload: Message content and data
        timestamp: Message creation time
        priority: Message priority level
        error: Error message if applicable
        metadata: Additional contextual information
        workflow_id: Optional workflow identifier for multi-step processes
        parent_trace_id: Optional parent trace for nested operations
    """
    sender: str
    receiver: str
    type: str
    trace_id: str
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    priority: MessagePriority = MessagePriority.NORMAL
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    workflow_id: Optional[str] = None
    parent_trace_id: Optional[str] = None
    
    @classmethod
    def create(cls, sender: str, receiver: str, msg_type: str, payload: Dict[str, Any], 
               priority: MessagePriority = MessagePriority.NORMAL, metadata: Optional[Dict[str, Any]] = None,
               trace_id: Optional[str] = None, workflow_id: Optional[str] = None,
               parent_trace_id: Optional[str] = None):
        """Create a new MCP message"""
        return cls(
            sender=sender,
            receiver=receiver,
            type=msg_type,
            trace_id=trace_id or str(uuid.uuid4()),
            payload=payload,
            priority=priority,
            metadata=metadata or {},
            workflow_id=workflow_id,
            parent_trace_id=parent_trace_id
        )
    
    @classmethod
    def create_error(cls, sender: str, receiver: str, error_msg: str, trace_id: Optional[str] = None):
        """Create an error message"""
        return cls(
            sender=sender,
            receiver=receiver,
            type=MessageType.ERROR.value,
            trace_id=trace_id or str(uuid.uuid4()),
            payload={"error": error_msg},
            error=error_msg,
            priority=MessagePriority.HIGH
        )
    
    def is_error(self) -> bool:
        """Check if this is an error message"""
        return self.type == MessageType.ERROR.value or self.error is not None
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to the message"""
        self.metadata[key] = value
    
    def get_age_seconds(self) -> float:
        """Get message age in seconds"""
        return time.time() - self.timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary representation"""
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "type": self.type,
            "trace_id": self.trace_id,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "priority": self.priority.value if isinstance(self.priority, MessagePriority) else self.priority,
            "error": self.error,
            "metadata": self.metadata,
            "workflow_id": self.workflow_id,
            "parent_trace_id": self.parent_trace_id
        }
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPMessage':
        """Create message from dictionary representation"""
        # Convert priority value to enum if needed
        priority = data.get('priority')
        if isinstance(priority, int):
            for p in MessagePriority:
                if p.value == priority:
                    priority = p
                    break
        
        return cls(
            sender=data['sender'],
            receiver=data['receiver'],
            type=data['type'],
            trace_id=data['trace_id'],
            payload=data['payload'],
            timestamp=data.get('timestamp', time.time()),
            priority=priority,
            error=data.get('error'),
            metadata=data.get('metadata', {}),
            workflow_id=data.get('workflow_id'),
            parent_trace_id=data.get('parent_trace_id')
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MCPMessage':
        """Create message from JSON string"""
        return cls.from_dict(json.loads(json_str))


class MCPBroker:
    """
    Message broker for MCP communication
    
    Handles message routing between agents using callbacks and workflow management
    """
    def __init__(self):
        self.handlers: Dict[str, Dict[str, List[Callable]]] = {}
        self.message_history: List[MCPMessage] = []
        self.max_history = 1000
        self.workflows: Dict[str, Dict[str, Any]] = {}  # Track active workflows
        self.agent_registry: Dict[str, Dict[str, Any]] = {}  # Track registered agents
        self.stats = {
            "messages_sent": 0,
            "messages_processed": 0,
            "errors": 0,
            "workflows_started": 0,
            "workflows_completed": 0
        }
    
    def register_handler(self, receiver: str, msg_type: str, handler: Callable[[MCPMessage], None]):
        """Register a message handler for a specific receiver and message type"""
        if receiver not in self.handlers:
            self.handlers[receiver] = {}
        
        if msg_type not in self.handlers[receiver]:
            self.handlers[receiver][msg_type] = []
        
        self.handlers[receiver][msg_type].append(handler)
        logger.debug(f"Registered handler for {receiver}/{msg_type}")
    
    def send(self, message: MCPMessage) -> bool:
        """Send a message to its intended receiver"""
        # Add to history
        self._add_to_history(message)
        
        # Update stats
        self.stats["messages_sent"] += 1
        
        # Track workflow if applicable
        if message.workflow_id:
            self._track_workflow_message(message)
        
        # Log message
        logger.debug(f"MCP message: {message.sender} → {message.receiver} ({message.type}) [trace: {message.trace_id}]")
        
        # Handle broadcast messages
        if message.receiver == "*":
            return self._broadcast_message(message)
        
        # Find handlers
        if message.receiver not in self.handlers:
            logger.warning(f"No handlers registered for receiver: {message.receiver}")
            self.stats["errors"] += 1
            return False
        
        if message.type not in self.handlers[message.receiver]:
            logger.warning(f"No handlers registered for message type: {message.type} to {message.receiver}")
            self.stats["errors"] += 1
            return False
        
        # Call handlers
        success = True
        for handler in self.handlers[message.receiver][message.type]:
            try:
                handler(message)
                self.stats["messages_processed"] += 1
            except Exception as e:
                logger.error(f"Error in message handler: {str(e)}")
                self.stats["errors"] += 1
                success = False
        
        return success
    
    def _add_to_history(self, message: MCPMessage):
        """Add message to history with size limit"""
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)
    
    def _broadcast_message(self, message: MCPMessage) -> bool:
        """Broadcast message to all registered agents"""
        success = True
        for agent_id in self.agent_registry.keys():
            if agent_id != message.sender:  # Don't send to sender
                # Create a copy of the message for each receiver
                broadcast_msg = MCPMessage.create(
                    sender=message.sender,
                    receiver=agent_id,
                    msg_type=message.type,
                    payload=message.payload,
                    priority=message.priority,
                    metadata=message.metadata,
                    trace_id=message.trace_id,
                    workflow_id=message.workflow_id,
                    parent_trace_id=message.parent_trace_id
                )
                if not self.send(broadcast_msg):
                    success = False
        return success
    
    def _track_workflow_message(self, message: MCPMessage):
        """Track workflow progress"""
        workflow_id = message.workflow_id
        
        if workflow_id not in self.workflows:
            self.workflows[workflow_id] = {
                "id": workflow_id,
                "started_at": time.time(),
                "messages": [],
                "status": "active",
                "participants": set()
            }
            self.stats["workflows_started"] += 1
        
        workflow = self.workflows[workflow_id]
        workflow["messages"].append({
            "trace_id": message.trace_id,
            "sender": message.sender,
            "receiver": message.receiver,
            "type": message.type,
            "timestamp": message.timestamp
        })
        workflow["participants"].add(message.sender)
        workflow["participants"].add(message.receiver)
        
        # Check if workflow is complete
        if message.type == MessageType.WORKFLOW_COMPLETE.value:
            workflow["status"] = "completed"
            workflow["completed_at"] = time.time()
            self.stats["workflows_completed"] += 1
    
    def register_agent(self, agent_id: str, agent_info: Dict[str, Any]):
        """Register an agent with the broker"""
        self.agent_registry[agent_id] = {
            **agent_info,
            "registered_at": time.time(),
            "last_seen": time.time()
        }
        logger.info(f"Registered agent: {agent_id}")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the broker"""
        if agent_id in self.agent_registry:
            del self.agent_registry[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific workflow"""
        return self.workflows.get(workflow_id)
    
    def get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get all active workflows"""
        return [w for w in self.workflows.values() if w["status"] == "active"]
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a registered agent"""
        return self.agent_registry.get(agent_id)
    
    def get_registered_agents(self) -> List[str]:
        """Get list of registered agent IDs"""
        return list(self.agent_registry.keys())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get broker statistics"""
        return {
            **self.stats,
            "registered_agents": len(self.agent_registry),
            "active_workflows": len([w for w in self.workflows.values() if w["status"] == "active"]),
            "total_workflows": len(self.workflows),
            "message_history_size": len(self.message_history)
        }
    
    def get_recent_messages(self, limit: int = 10, agent_id: Optional[str] = None, 
                          msg_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent message history with optional filtering"""
        messages = self.message_history
        
        # Filter by agent if specified
        if agent_id:
            messages = [m for m in messages if m.sender == agent_id or m.receiver == agent_id]
        
        # Filter by message type if specified
        if msg_type:
            messages = [m for m in messages if m.type == msg_type]
        
        # Get recent messages
        recent = messages[-limit:] if messages else []
        
        return [
            {
                "trace_id": msg.trace_id,
                "sender": msg.sender,
                "receiver": msg.receiver,
                "type": msg.type,
                "timestamp": msg.timestamp,
                "is_error": msg.is_error(),
                "age_seconds": msg.get_age_seconds(),
                "workflow_id": msg.workflow_id,
                "parent_trace_id": msg.parent_trace_id
            }
            for msg in recent
        ]


# Global broker instance
broker = MCPBroker()