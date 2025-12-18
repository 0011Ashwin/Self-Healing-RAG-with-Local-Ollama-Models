
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.healing import smart_query
from modules.vector_db import load_vector_db
from modules.logger import setup_logger

def main():
    logger, log_path = setup_logger()
    logger.info("--- Self-Healing RAG System Started ---")
    print(f"Logs are being saved to: {log_path}")
    
    # Initial check (optional, smart_query handles it, but good for startup)
    vector_store = load_vector_db()
    if not vector_store:
        logger.warning("System Startup: VectorDB not found. It will be created on first query if needed.")

    while True:
        query = input("\nEnter your question (or 'quit'): ")
        if query.lower() in ['quit', 'exit']:
            logger.info("User requested exit.")
            break
        
        response = smart_query(query, logger) # Pass logger to smart_query
        print("\nANSWER:")
        try:
            print(response)
        except UnicodeEncodeError:
            print(response.encode('utf-8', errors='ignore').decode('utf-8'))

if __name__ == "__main__":
    main()
