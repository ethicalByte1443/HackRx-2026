import numpy as np

def search_top_k_clauses(query: str, model, faiss_index, clauses, k=5):
    query_vector = model.encode([query])
    distances, indices = faiss_index.search(np.array(query_vector), k)
    return [clauses[i] for i in indices[0]]
