# Project Review: Self-Healing RAG with Local Ollama Models

## 1. Project Overview
The **Self-Healing RAG (Retrieval-Augmented Generation)** project is a local, privacy-focused AI system designed to answer questions based on your personal documents (PDFs). It distinguishes itself with "self-healing" capabilities, meaning it can automatically detect and resolve common runtime issues like missing databases or empty search results without user intervention.

## 2. Key Features
-   **Fully Local Operation**: Utilizes Ollama to run LLMs (`phi3`) and embedding models (`nomic-embed-text`) entirely on your machine. No data leaves your system.
-   **Self-Healing Architecture**:
    -   **Vector DB Restoration**: Automatically detects if the vector store is missing or corrupt and triggers a re-ingestion pipeline.
    -   **Retrieval Correction**: If a search yields no results, it attempts to re-index the data to ensure nothing was missed.
-   **PDF Ingestion**: Automatically scans the `data/` directory for PDF files, extracts text, chunks it, and builds a searchable index.

## 3. Technology Stack
-   **Language**: Python 3.10+
-   **Framework**: LangChain (for orchestration and RAG logic)
-   **LLM Provider**: Ollama (Local API)
    -   **Generation Model**: `phi3:mini` (Lightweight, efficient instruction-tuned model)
    -   **Embedding Model**: `nomic-embed-text` (High-quality text embeddings)
-   **Vector Database**: ChromaDB (Local, persistent vector storage)
-   **Core Libraries**: `langchain-ollama`, `pypdf`, `tiktoken`

## 4. Architecture & Workflow

### A. Data Ingestion (ETL Pipeline)
1.  **Load (`etl/loader.py`)**: The system scans `data/*.pdf` using `PyPDFLoader` to extract raw text pages.
2.  **Chunk (`etl/chunker.py`)**: Text is split into smaller, manageable chunks (1000 characters) with overlap (200 characters) to preserve context.
3.  **Embed & Store (`modules/vector_db.py`)**: Chunks are converted into vector embeddings using `nomic-embed-text` and stored in ChromaDB (`vectorstore/` directory).

### B. Retrieval & Generation (RAG Pipeline)
1.  **Query**: User inputs a question via `main.py`.
2.  **Retrieve (`modules/retriever.py`)**: The system searches the Vector DB for the most relevant text chunks (top-k similarity search).
3.  **Generate (`modules/generator.py`)**: The retrieved context and the user's question are sent to `phi3:mini`. The model generates a natural language answer based *only* on the provided context.

### C. Self-Healing Mechanism (`modules/healing.py`)
This is the "brain" of the system. It wraps the standard query process:
1.  **Pre-Check**: Before querying, it checks if the Vector DB exists and has data.
2.  **Healing Action**: If the DB is missing/empty, it calls `heal_vector_store()`, which triggers the ETL pipeline on the fly.
3.  **Post-Retrieval Check**: If the retriever returns 0 documents, it infers a sync issue and re-runs ingestion to ensuring fresh data is available.

## 5. File Structure Breakdown
```
D:\Self-healing-RAG\
├── data/                  # Source PDF documents
├── etl/                   # Extract, Transform, Load scripts
│   ├── loader.py          # Loads PDFs
│   └── chunker.py         # Splits text
├── logs/                  # System logs
├── modules/               # Core Application Logic
│   ├── config.py          # Central configuration (Paths, Model Names)
│   ├── embeddings.py      # Embedding model setup (Ollama)
│   ├── generator.py       # LLM generation setup (Ollama)
│   ├── healing.py         # Self-healing logic & orchestration
│   ├── logger.py          # Logging setup
│   ├── retriever.py       # Search logic
│   └── vector_db.py       # ChromaDB management
├── vectorstore/           # Persisted Vector Database
├── main.py                # Entry point script
├── list_models.py         # Utility to check available Ollama models
├── requirements.txt       # Python dependencies
└── README.md              # Quick start guide
```

## 6. Future Recommendations
-   **Model Experimentation**: You can easily swap `phi3` for `mistral` or `llama3` in `modules/config.py` if you need more capability (requires more RAM).
-   **UI Upgrade**: Currently a CLI tool, this could be wrapped in a Streamlit or Chainlit web interface for a better user experience.
-   **Advanced Healing**: Implement "Query Transformation" (rewriting user queries) if the initial search fails, rather than just re-ingesting data.
