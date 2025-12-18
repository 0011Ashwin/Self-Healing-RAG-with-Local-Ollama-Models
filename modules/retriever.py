
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_retriever(vector_store, search_type="similarity", k=4):
    retriever = vector_store.as_retriever(
        search_type=search_type,
        search_kwargs={"k": k}
    )
    return retriever

def get_advanced_retriever(vector_store):
    # Example of a more advanced retriever logic if needed (e.g. compression)
    # For now, we will stick to the basic one as the base, self-healing will add logic on top
    return get_retriever(vector_store)
