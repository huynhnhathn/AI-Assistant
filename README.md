# RAG Application

A comprehensive **Retrieval-Augmented Generation (RAG)** application built with LangChain, Qdrant vector database, and OpenAI.

## 🚀 Features

- **Multi-format Document Processing**: Support for PDF, DOCX, TXT, MD, HTML, and more
- **Vector Similarity Search**: Powered by Qdrant vector database
- **Conversational Memory**: Maintains context across conversations
- **Multiple Interfaces**: CLI, Web UI (Streamlit), and programmatic API
- **Flexible Document Sources**: Files, directories, URLs, and direct uploads
- **Real-time Chat**: Interactive chat interface with source citations
- **System Monitoring**: Health checks and status monitoring

## 🏗️ Architecture

```
├── src/rag_app/
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   ├── vector_store.py    # Qdrant integration
│   │   ├── document_processor.py # Document loading & chunking
│   │   └── rag_chain.py       # Main RAG implementation
│   └── utils/
│       └── logging_config.py  # Logging configuration
├── examples/
│   ├── sample_document.txt    # Sample document for testing
│   ├── run_example.py         # Programmatic usage example
│   └── streamlit_app.py       # Web interface
├── data/
│   ├── documents/             # Document storage
│   └── processed/             # Processed document cache
├── main.py                    # CLI application
├── requirements.txt           # Dependencies
└── .env.example              # Environment template
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Qdrant vector database (local or cloud)
- OpenAI API key

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd rag-application
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start Qdrant** (if running locally):
   ```bash
   # Using Docker
   docker run -p 6333:6333 qdrant/qdrant
   
   # Or using Docker Compose
   docker-compose up -d qdrant
   ```

### Environment Configuration

Edit `.env` file with your settings:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key_here

# Application Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EMBEDDING_MODEL=text-embedding-ada-002
LLM_MODEL=gpt-3.5-turbo
TEMPERATURE=0.7
MAX_TOKENS=1000

# Collection Configuration
COLLECTION_NAME=rag_documents
```

## 🚀 Usage

### Command Line Interface

The main CLI provides several commands:

#### Add Documents
```bash
# Add a single file
python main.py add-documents path/to/document.pdf

# Add all documents from a directory
python main.py add-documents path/to/documents/ --type directory

# Add from URL
python main.py add-documents https://example.com/document.html --type url
```

#### Query the System
```bash
# Simple query
python main.py query "What is machine learning?"

# Query with memory (conversational)
python main.py query "What is supervised learning?" --memory

# Specify number of sources
python main.py query "Explain deep learning" --sources 6
```

#### Interactive Chat
```bash
python main.py interactive
```

#### System Status
```bash
python main.py status
```

#### Application Info
```bash
python main.py info
```

### Web Interface (Streamlit)

Launch the web interface:

```bash
streamlit run examples/streamlit_app.py
```

Features:
- **Chat Interface**: Interactive conversation with the RAG system
- **Document Upload**: Drag-and-drop file uploads
- **URL Processing**: Add documents from web URLs
- **Directory Processing**: Bulk process document directories
- **System Status**: Real-time system health monitoring
- **Settings**: Configurable query parameters

### Programmatic Usage

```python
from src.rag_app.core.rag_chain import RAGChain

# Initialize RAG system
rag = RAGChain()

# Add documents
result = rag.add_documents_from_source(
    source="path/to/document.pdf",
    source_type="file"
)

# Query the system
result = rag.query(
    question="What is the main topic of the document?",
    k=4,  # Number of source chunks
    use_memory=True  # Enable conversational memory
)

print(result["answer"])
```

### Example Script

Run the provided example:

```bash
python examples/run_example.py
```

This demonstrates:
- Document processing
- Various query types
- Conversational mode
- System status checking

## 📊 Supported Document Types

| Format | Extension | Loader |
|--------|-----------|---------|
| PDF | `.pdf` | PyPDFLoader |
| Word | `.docx` | Docx2txtLoader |
| Text | `.txt` | TextLoader |
| Markdown | `.md` | TextLoader |
| HTML | `.html` | TextLoader |
| Python | `.py` | TextLoader |
| JavaScript | `.js` | TextLoader |
| JSON | `.json` | TextLoader |
| CSV | `.csv` | TextLoader |
| Web Pages | URLs | WebBaseLoader |

## 🔧 Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `CHUNK_SIZE` | Size of text chunks | 1000 |
| `CHUNK_OVERLAP` | Overlap between chunks | 200 |
| `EMBEDDING_MODEL` | OpenAI embedding model | text-embedding-ada-002 |
| `LLM_MODEL` | OpenAI chat model | gpt-3.5-turbo |
| `TEMPERATURE` | LLM temperature | 0.7 |
| `MAX_TOKENS` | Maximum response tokens | 1000 |
| `COLLECTION_NAME` | Qdrant collection name | rag_documents |

## 🔍 How It Works

1. **Document Processing**: Documents are loaded, split into chunks, and embedded using OpenAI embeddings
2. **Vector Storage**: Embeddings are stored in Qdrant vector database for similarity search
3. **Query Processing**: User queries are embedded and used to find similar document chunks
4. **Response Generation**: Retrieved chunks provide context for OpenAI to generate responses
5. **Memory Management**: Conversation history is maintained for contextual responses

## 🛡️ Error Handling

The application includes comprehensive error handling:

- **Configuration validation** on startup
- **Graceful handling** of missing documents
- **Retry logic** for API calls
- **Detailed logging** for debugging
- **Status monitoring** for system health

## 📝 Logging

Logs are configured with different levels:

```bash
# Enable verbose logging
python main.py --verbose query "What is AI?"

# Log to file
python main.py --log-file app.log query "What is AI?"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Dependencies

- **LangChain**: LLM application framework
- **Qdrant**: Vector database
- **OpenAI**: Language models and embeddings
- **Streamlit**: Web interface
- **Click**: CLI framework
- **Rich**: Terminal formatting
- **PyPDF2**: PDF processing
- **python-docx**: Word document processing

## 🚨 Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY is required"**
   - Ensure your OpenAI API key is set in the `.env` file

2. **"Failed to connect to Qdrant"**
   - Check if Qdrant is running on the specified URL
   - Verify network connectivity

3. **"No documents found"**
   - Check file paths and permissions
   - Verify supported file formats

4. **Memory issues with large documents**
   - Reduce `CHUNK_SIZE` in configuration
   - Process documents in smaller batches

### Performance Tips

- Use SSD storage for better I/O performance
- Increase `CHUNK_SIZE` for longer context (but watch token limits)
- Use GPU-enabled Qdrant for faster similarity search
- Consider using faster embedding models for large-scale deployments

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the logs for detailed error messages
- Open an issue on the repository