
import os
from langchain_community.document_loaders import PyPDFLoader
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.config import DATA_DIR

def load_pdfs(data_dir=DATA_DIR):
    documents = []
    if not os.path.exists(data_dir):
        print(f"Data directory {data_dir} does not exist.")
        return []
    
    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(data_dir, filename)
            print(f"Loading {filename}...")
            try:
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    return documents

if __name__ == "__main__":
    docs = load_pdfs()
    print(f"Loaded {len(docs)} pages.")
