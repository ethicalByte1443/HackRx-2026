from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_clauses(clauses):
    return model.encode(clauses)
