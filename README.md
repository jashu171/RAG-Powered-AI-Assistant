# Agentic RAG Chatbot with Model Context Protocol (MCP)

A sophisticated multi-agent Retrieval-Augmented Generation (RAG) system that processes multi-format documents and answers user queries using an agentic architecture with Model Context Protocol (MCP) for inter-agent communication.

## 🧠 Sample Workflow (Message Passing with MCP)

```
User uploads: sales_review.pdf, metrics.csv
User: "What KPIs were tracked in Q1?"
➡️ UI forwards to CoordinatorAgent
➡️ Coordinator triggers:
   🔸 IngestionAgent → parses documents
   🔸 RetrievalAgent → finds relevant chunks  
   🔸 LLMResponseAgent → formats prompt & calls LLM
➡️ Chatbot shows answer + source chunks
```

**MCP Message Example:**
```json
{
  "type": "RETRIEVAL_RESULT",
  "sender": "RetrievalAgent", 
  "receiver": "LLMResponseAgent",
  "trace_id": "rag-457",
  "payload": {
    "retrieved_context": [
      "slide 3: revenue up 15% in Q1",
      "doc: Q1 summary shows KPIs tracked..."
    ],
    "query": "What KPIs were tracked in Q1?"
  }
}
```

## 🚀 Key Features

### Multi-Agent Architecture
- **Coordinator Agent**: Orchestrates the entire pipeline and manages agent communication
- **Ingestion Agent**: Processes and parses documents from multiple formats
- **Retrieval Agent**: Manages vector storage and semantic search
- **LLM Response Agent**: Generates contextual responses using Google Gemini

### Enhanced Document Processing
- **Multi-format Support**: PDF, DOCX, PPTX, CSV, TXT, MD
- **Intelligent Chunking**: Advanced text segmentation with overlap strategies
- **Metadata Preservation**: Maintains document structure and source information
- **Error Handling**: Robust processing with detailed error reporting

### Advanced Vector Storage
- **ChromaDB Integration**: Persistent vector storage with metadata
- **Semantic Search**: Enhanced search with similarity scoring
- **File-based Filtering**: Search within specific documents
- **Collection Management**: Clear, update, and manage document collections

### Model Context Protocol (MCP)
- **Structured Messaging**: Type-safe inter-agent communication
- **Message Tracing**: Full request tracing with unique IDs
- **Error Propagation**: Comprehensive error handling across agents
- **Priority Handling**: Message prioritization and routing

### Production-Ready Features
- **Health Monitoring**: System health checks and agent status
- **Statistics Tracking**: Comprehensive performance metrics
- **Logging**: Structured logging with multiple handlers
- **Configuration Management**: Environment-based configuration
- **API Documentation**: RESTful API with proper error responses

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Client    │◄──►│  Flask Web API   │◄──►│  Coordinator    │
└─────────────────┘    └──────────────────┘    │     Agent       │
                                                └─────────┬───────┘
                                                          │
                       ┌──────────────────────────────────┼──────────────────────────────────┐
                       │                                  │                                  │
                       ▼                                  ▼                                  ▼
              ┌─────────────────┐                ┌─────────────────┐                ┌─────────────────┐
              │  Ingestion      │                │   Retrieval     │                │  LLM Response   │
              │    Agent        │                │     Agent       │                │     Agent       │
              └─────────┬───────┘                └─────────┬───────┘                └─────────────────┘
                        │                                  │
                        ▼                                  ▼
              ┌─────────────────┐                ┌─────────────────┐
              │  Document       │                │  Vector Store   │
              │   Parser        │                │   (ChromaDB)    │
              └─────────────────┘                └─────────────────┘
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Google Gemini API Key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agentic-rag-mcp
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   # Main application with MCP support
   python app.py
   
   # MCP workflow demonstration
   python mcp_workflow_example.py
   ```

## 🔧 Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional - Agent Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
DEFAULT_SEARCH_K=5
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=gemini-2.0-flash

# Optional - System Configuration
MAX_FILE_SIZE_MB=32
UPLOAD_FOLDER=uploads
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
```

### MCP Configuration

The system supports MCP configuration via `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "rag-mcp": {
      "command": "uvx",
      "args": ["agentic-rag-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "INFO"
      },
      "disabled": false,
      "autoApprove": ["send_message", "receive_messages", "health_check"]
    }
  }
}
```

### Configuration File

The system uses `config.py` for centralized configuration management:

```python
from config import config

# Access agent configuration
chunk_size = config.agent.chunk_size
search_k = config.agent.default_search_k

# Access system configuration
max_file_size = config.system.max_file_size_mb
```

## 📚 API Documentation

### Upload Documents
```http
POST /upload
Content-Type: multipart/form-data

files: [file1.pdf, file2.docx, ...]
```

**Response:**
```json
{
  "uploaded_files": ["file1.pdf", "file2.docx"],
  "failed_files": [],
  "processing_results": [
    {
      "filename": "file1.pdf",
      "chunks_processed": 15,
      "processing_time": 2.34,
      "trace_id": "uuid-here"
    }
  ],
  "message": "Successfully processed 2 files"
}
```

### Query Documents
```http
POST /query
Content-Type: application/json

{
  "query": "What is the main topic discussed?",
  "search_k": 5
}
```

**Response:**
```json
{
  "answer": "Based on the uploaded documents...",
  "context_chunks": ["chunk1", "chunk2", "chunk3"],
  "sources_used": 3,
  "response_type": "rag",
  "collection_size": 45,
  "processing_time": 1.23,
  "trace_id": "uuid-here",
  "metadata": {
    "query_length": 35,
    "search_k": 5,
    "timestamp": "2024-01-01T12:00:00"
  }
}
```

### System Health
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "system_health": {
    "overall_status": "healthy",
    "agent_health": {
      "ingestion": {"status": "healthy", "stats": {...}},
      "retrieval": {"status": "healthy", "stats": {...}},
      "llm": {"status": "healthy", "stats": {...}}
    }
  }
}
```

### System Statistics
```http
GET /stats
```

### Clear Documents
```http
POST /clear
```

## 🔍 Model Context Protocol (MCP)

The system implements a sophisticated MCP for agent communication:

### Message Structure
```python
@dataclass
class MCPMessage:
    sender: str
    receiver: str
    type: str
    trace_id: str
    payload: Dict[str, Any]
    timestamp: float
    priority: MessagePriority
    error: Optional[str]
    metadata: Dict[str, Any]
```

### Message Types
- `DOCUMENT_PROCESSED`: Document ingestion complete
- `DOCUMENTS_INDEXED`: Vector indexing complete
- `CONTEXT_RESPONSE`: Retrieval results
- `RESPONSE_GENERATED`: LLM response ready
- `ERROR`: Error occurred
- `HEALTH_CHECK`: Agent health status

### Error Handling
- Automatic error propagation between agents
- Graceful degradation (general responses when RAG fails)
- Comprehensive error logging and tracing

## 📊 Monitoring & Observability

### Logging
- Structured logging with timestamps and trace IDs
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- File and console output

### Metrics
- Document processing statistics
- Query response times
- Agent health status
- Vector store metrics

### Health Checks
- Individual agent health monitoring
- System-wide health aggregation
- API connectivity testing

## 🚀 Advanced Features

### Intelligent Document Chunking
- Sentence-boundary aware chunking
- Configurable chunk size and overlap
- Metadata preservation
- Structure-aware parsing (headings, slides, etc.)

### Enhanced Search
- Semantic similarity search
- Metadata-based filtering
- File-specific search
- Configurable result count

### Response Generation
- Context-aware prompting
- Source attribution
- Fallback to general responses
- Response type classification

## 🔒 Security Considerations

- File type validation
- Size limits enforcement
- Secure filename handling
- API key protection
- Input sanitization

## 🧪 Testing

### Quick Start
```bash
# Run the MCP workflow demonstration
python mcp_workflow_example.py

# Start the main application
python app.py

# Test basic MCP functionality
python test_mcp_basic.py
```

### Testing with Web Interface
1. Upload test documents via the web interface
2. Ask questions about the content
3. Monitor system health at `/health`
4. Check statistics at `/stats`

### MCP Testing
```bash
# Test MCP REST API (optional)
python mcp_rest_api.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **API Key Error**: Ensure `GEMINI_API_KEY` is set in `.env`
2. **File Upload Fails**: Check file size limits and supported formats
3. **No Search Results**: Verify documents are properly indexed
4. **Memory Issues**: Reduce chunk size or file count

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python app.py
```

### Health Monitoring

Check system status:
```bash
curl http://localhost:8000/health
```

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `app.log`
3. Open an issue on GitHub
4. Contact the development team

---

**Built with ❤️ using Python, Flask, ChromaDB, and Google Gemini**