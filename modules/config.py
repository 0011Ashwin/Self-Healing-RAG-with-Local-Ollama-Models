
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GOOGLE_API_KEY:
    print("Warning: GOOGLE_API_KEY not found in .env")
if not GROQ_API_KEY:
    print("Warning: GROQ_API_KEY not found in .env")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vectorstore")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = "nomic-embed-text" # Ollama Embedding
LLM_MODEL = "phi3:mini" # Ollama Model
