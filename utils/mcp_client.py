"""
Model Context Protocol (MCP) Client

This module provides a client library for agents to communicate using MCP.
It supports both in-memory and REST API communication.
"""

import requests
import logging
from typing import Dict, Any, List, Optional, Callable
from .mcp import MCPMessage, MessageType, MessagePriority, broker

logger = logging.getLogger(__name__)

class MCPClient:
    """
    MCP client for agent communication
    
    Supports both in-memory and REST API communication
    """
    
    def __init__(self, agent_id: str, api_url: Optional[str] = None):
        """
        Initialize MCP client
        
        Args:
            agent_id: Identifier for this agent
            api_url: URL of MCP REST API (None for in-memory only)
        """
        self.agent_id = agent_id
        self.api_url = api_url
        self.handlers: Dict[str, Callable[[MCPMessage], None]] = {}
        self.use_rest = api_url is not None
        
        logger.info(f"Initialized MCP client for {agent_id} (REST API: {'enabled' if self.use_rest else 'disabled'})")
    
    def register_handler(self, msg_type: str, handler: Callable[[MCPMessage], None]):
        """
        Register a handler for a specific message type
        
        Args:
            msg_type: Message type to handle
            handler: Function to call when message is received
        """
        # Register with local broker
        broker.register_handler(self.agent_id, msg_type, handler)
        
        # Store handler for polling
        self.handlers[msg_type] = handler
        
        logger.debug(f"Registered handler for {msg_type}")
    
    def send(self, receiver: str, msg_type: str, payload: Dict[str, Any], 
             priority: MessagePriority = MessagePriority.NORMAL, 
             metadata: Optional[Dict[str, Any]] = None,
             trace_id: Optional[str] = None) -> MCPMessage:
        """
        Send a message to another agent
        
        Args:
            receiver: Target agent identifier
            msg_type: Message type
            payload: Message content
            priority: Message priority
            metadata: Additional contextual information
            trace_id: Optional trace ID for message tracking
            
        Returns:
            The sent message
        """
        # Create message
        message = MCPMessage.create(
            sender=self.agent_id,
            receiver=receiver,
            msg_type=msg_type,
            payload=payload,
            priority=priority,
            metadata=metadata,
            trace_id=trace_id
        )
        
        # Send message
        if self.use_rest:
            self._send_rest(message)
        else:
            broker.send(message)
        
        return message
    
    def send_error(self, receiver: str, error_msg: str, trace_id: Optional[str] = None) -> MCPMessage:
        """
        Send an error message
        
        Args:
            receiver: Target agent identifier
            error_msg: Error message
            trace_id: Optional trace ID for message tracking
            
        Returns:
            The sent message
        """
        # Create error message
        message = MCPMessage.create_error(
            sender=self.agent_id,
            receiver=receiver,
            error_msg=error_msg,
            trace_id=trace_id
        )
        
        # Send message
        if self.use_rest:
            self._send_rest(message)
        else:
            broker.send(message)
        
        return message
    
    def reply(self, original_msg: MCPMessage, msg_type: str, payload: Dict[str, Any],
              priority: MessagePriority = MessagePriority.NORMAL,
              metadata: Optional[Dict[str, Any]] = None) -> MCPMessage:
        """
        Reply to a message
        
        Args:
            original_msg: Original message to reply to
            msg_type: Message type
            payload: Message content
            priority: Message priority
            metadata: Additional contextual information
            
        Returns:
            The sent message
        """
        # Create metadata if not provided
        if metadata is None:
            metadata = {}
        
        # Add original message trace ID to metadata
        metadata["original_trace_id"] = original_msg.trace_id
        
        # Send reply
        return self.send(
            receiver=original_msg.sender,
            msg_type=msg_type,
            payload=payload,
            priority=priority,
            metadata=metadata,
            trace_id=original_msg.trace_id
        )
    
    def poll(self, timeout: float = 0.1) -> List[MCPMessage]:
        """
        Poll for messages (only used with REST API)
        
        Args:
            timeout: Request timeout in seconds
            
        Returns:
            List of received messages
        """
        if not self.use_rest:
            logger.warning("Polling not needed for in-memory communication")
            return []
        
        try:
            # Get messages from REST API
            response = requests.get(
                f"{self.api_url}/receive/{self.agent_id}",
                timeout=timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to poll messages: {response.text}")
                return []
            
            data = response.json()
            messages = []
            
            # Process messages
            for msg_data in data.get("messages", []):
                try:
                    message = MCPMessage.from_dict(msg_data)
                    messages.append(message)
                    
                    # Call handler if registered
                    if message.type in self.handlers:
                        self.handlers[message.type](message)
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
            
            return messages
            
        except Exception as e:
            logger.error(f"Error polling messages: {str(e)}")
            return []
    
    def _send_rest(self, message: MCPMessage):
        """Send message using REST API"""
        try:
            response = requests.post(
                f"{self.api_url}/send",
                json=message.to_dict(),
                headers={"Content-Type": "application/json"},
                timeout=5.0
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to send message: {response.text}")
                
        except Exception as e:
            logger.error(f"Error sending message via REST: {str(e)}")
            # Fall back to in-memory
            logger.info("Falling back to in-memory messaging")
            broker.send(message)


class MCPAgent:
    """
    Base class for MCP-enabled agents
    
    Provides common functionality for MCP communication
    """
    
    def __init__(self, agent_id: str, api_url: Optional[str] = None):
        """
        Initialize MCP agent
        
        Args:
            agent_id: Identifier for this agent
            api_url: URL of MCP REST API (None for in-memory only)
        """
        self.agent_id = agent_id
        self.mcp = MCPClient(agent_id, api_url)
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "errors": 0
        }
        
        # Register default handlers
        self._register_default_handlers()
        
        logger.info(f"Initialized MCP agent: {agent_id}")
    
    def _register_default_handlers(self):
        """Register default message handlers"""
        # Health check handler
        self.mcp.register_handler(MessageType.HEALTH_CHECK.value, self._handle_health_check)
    
    def _handle_health_check(self, message: MCPMessage):
        """Handle health check messages"""
        logger.info(f"Health check received from {message.sender}")
        
        # Send health status
        self.mcp.reply(
            original_msg=message,
            msg_type=MessageType.AGENT_STATUS.value,
            payload={
                "status": "healthy",
                "agent_id": self.agent_id,
                "stats": self.stats
            }
        )
    
    def send_message(self, receiver: str, msg_type: str, payload: Dict[str, Any],
                    priority: MessagePriority = MessagePriority.NORMAL,
                    metadata: Optional[Dict[str, Any]] = None) -> MCPMessage:
        """
        Send a message to another agent
        
        Args:
            receiver: Target agent identifier
            msg_type: Message type
            payload: Message content
            priority: Message priority
            metadata: Additional contextual information
            
        Returns:
            The sent message
        """
        message = self.mcp.send(receiver, msg_type, payload, priority, metadata)
        self.stats["messages_sent"] += 1
        return message
    
    def send_error(self, receiver: str, error_msg: str) -> MCPMessage:
        """
        Send an error message
        
        Args:
            receiver: Target agent identifier
            error_msg: Error message
            
        Returns:
            The sent message
        """
        message = self.mcp.send_error(receiver, error_msg)
        self.stats["messages_sent"] += 1
        self.stats["errors"] += 1
        return message
    
    def reply_to(self, original_msg: MCPMessage, msg_type: str, payload: Dict[str, Any],
                priority: MessagePriority = MessagePriority.NORMAL,
                metadata: Optional[Dict[str, Any]] = None) -> MCPMessage:
        """
        Reply to a message
        
        Args:
            original_msg: Original message to reply to
            msg_type: Message type
            payload: Message content
            priority: Message priority
            metadata: Additional contextual information
            
        Returns:
            The sent message
        """
        message = self.mcp.reply(original_msg, msg_type, payload, priority, metadata)
        self.stats["messages_sent"] += 1
        return message
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return self.stats.copy()
    
    def health_check(self) -> Dict[str, Any]:
        """Get agent health status"""
        return {
            "status": "healthy",
            "agent_id": self.agent_id,
            "stats": self.get_stats()
        }