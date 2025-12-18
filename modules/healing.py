
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from etl.loader import load_pdfs
from etl.chunker import chunk_documents
from modules.vector_db import create_vector_db, load_vector_db
from modules.retriever import get_retriever
from modules.generator import generate_answer

def check_embeddings(vector_store):
    """
    Simple check to see if vector store has data.
    """
    try:
        # Checking if collection is empty
        count = vector_store._collection.count()
        if count == 0:
            return False, "Vector store is empty"
        return True, f"Vector store has {count} entries"
    except Exception as e:
        return False, f"Error checking vector store: {e}"

def heal_vector_store():
    """
    Re-runs the ingestion pipeline.
    """
    print("Healing: Re-ingesting data...")
    docs = load_pdfs()
    if not docs:
        print("Healing Failed: No documents found to ingest.")
        return None
    
    chunks = chunk_documents(docs)
    vector_store = create_vector_db(chunks)
    return vector_store

def analyze_logs(log_path):
    """
    Reads the current log file to find patterns.
    This is a mock implementation of 'reading logs to fix execution'.
    In a real scenario, this would parse for specific error codes or stack traces.
    """
    if not log_path or not os.path.exists(log_path):
        return
    
    with open(log_path, 'r') as f:
        logs = f.read()
    
    if "RESOURCE_EXHAUSTED" in logs:
        print("\n[Self-Correction Suggestion]: Log analysis detected Rate Limits. Suggestion: Increase wait time or switch providers.")
        # We could programmatically switch config here if we had multiple valid providers.

def smart_query(query, logger=None):
    """
    Orchestrates the query with self-healing capabilities.
    """
    if logger:
        logger.info(f"Processing query: {query}")
    else:
        print(f"Querying: {query}")
    
    # 1. Check Vector Store Health
    vector_store = load_vector_db()
    if not vector_store:
         if logger: logger.warning("Issue Detected: Vector DB missing. triggering self-healing...")
         vector_store = heal_vector_store()
    else:
        is_healthy, msg = check_embeddings(vector_store)
        if not is_healthy:
            if logger: logger.warning(f"Issue Detected: {msg}. Triggering self-healing...")
            # Release reference to free lock (important for Windows)
            del vector_store
            import gc
            gc.collect()
            vector_store = heal_vector_store()
            
    if not vector_store:
        msg = "System Critical Failure: Could not restore Vector DB."
        if logger: logger.error(msg)
        return msg

    # 2. Retrieval
    retriever = get_retriever(vector_store)
    docs = retriever.invoke(query)
    
    # 3. Retrieval Self-Correction (Simple)
    if not docs:
        if logger: logger.warning("Issue Detected: No documents retrieved. Creating stricter search or re-indexing...")
        # For now, let's just re-index if nothing is found, assuming corruption or empty
        # In a real system, we might try different search params first
        vector_store = heal_vector_store()
        retriever = get_retriever(vector_store)
        docs = retriever.invoke(query)
        
    if not docs:
        msg = "I could not find any relevant information even after self-correction."
        if logger: logger.info(msg)
        return msg

    # 4. Generation
    try:
        answer = generate_answer(query, retriever)
        if logger: logger.info("Answer generated successfully.")
        return answer
    except Exception as e:
        if logger: logger.error(f"Generation Error: {e}")
        return f"Error generating answer due to LLM failure: {e}"

