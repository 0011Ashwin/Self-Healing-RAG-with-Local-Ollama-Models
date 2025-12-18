
from langchain_ollama import OllamaEmbeddings
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.config import EMBEDDING_MODEL

def get_embeddings():
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
    )
    return embeddings
