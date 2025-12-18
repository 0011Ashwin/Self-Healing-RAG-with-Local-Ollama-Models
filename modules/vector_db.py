
from langchain_chroma import Chroma
import sys
import os
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.config import VECTOR_DB_DIR
from modules.embeddings import get_embeddings

def create_vector_db(chunks):
    if os.path.exists(VECTOR_DB_DIR):
        print("Vector DB exists. Deleting to refresh...")
        try:
            shutil.rmtree(VECTOR_DB_DIR)
        except OSError as e:
            print(f"Warning: Could not fully delete {VECTOR_DB_DIR}: {e}")
            # If we can't delete, we might still be able to overwrite or append.
            # But let's try to proceed.
    
    embeddings = get_embeddings()
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR
    )
    # vector_store.persist() # ChromaDB 0.4+ persists automatically
    print(f"Vector DB created at {VECTOR_DB_DIR} with {len(chunks)} chunks.")
    return vector_store

def load_vector_db():
    embeddings = get_embeddings()
    if not os.path.exists(VECTOR_DB_DIR):
        print("Vector DB not found.")
        return None
        
    vector_store = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embeddings
    )
    return vector_store
