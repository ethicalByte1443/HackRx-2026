import fitz  # PyMuPDF
import requests

# Step 1: Extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Step 2: Prepare inputs
user_query = "46-year-old male, knee surgery in Pune, 3-month-old insurance policy"
clause = extract_text_from_pdf("BAJHLIP23020V012223.pdf")[:2000]  # Limit size if large

# *******************************


doc = fitz.open("/content/sample_data/BAJHLIP23020V012223.pdf")
text = ""
for page in doc:
    text += page.get_text()
print(text[0:100])

import re

query = "46-year-old male, knee surgery in Pune, 3-month-old insurance policy"

age = re.search(r"(\d+)[ -]?year", query)
procedure = re.search(r"(knee|hip|eye|heart) surgery", query)
location = re.search(r"in (\w+)", query)
duration = re.search(r"(\d+)[ -]?month", query)

parsed_query = {
    "age": int(age.group(1)) if age else None,
    "procedure": procedure.group(0) if procedure else None,
    "location": location.group(1) if location else None,
    "policy_months": int(duration.group(1)) if duration else None
}



def extract_clauses_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"

    # Clause ke liye split kar rahe hain paragraph wise
    clauses = [clause.strip() for clause in full_text.split('\n') if len(clause.strip()) > 30]
    return clauses

# Call function with your file
clause = extract_clauses_from_pdf("/content/sample_data/BAJHLIP23020V012223.pdf")

from sentence_transformers import SentenceTransformer

# Load pre-trained Hugging Face model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Ye 'clauses' list aapne Step 4.1 mein extract ki thi from PDF
# Example: clauses = ["Knee surgery is covered...", "Dental is not covered...", ...]

# Convert each clause into a 384-dimensional vector
clause_embeddings = model.encode(clause)

# Optional: Show embedding shape for confirmation


import faiss
import numpy as np

# Assumption: 'clause_embeddings' is already generated from Step 4.2

# Convert embeddings list to numpy array (FAISS uses numpy)
clause_embeddings_np = np.array(clause_embeddings)

# Dimensions of each vector
dimension = clause_embeddings_np.shape[1]

# Create FAISS index (Flat index using L2 distance)
index = faiss.IndexFlatL2(dimension)

# Add all clause embeddings to FAISS index
index.add(clause_embeddings_np)

# Step 1: User query
query = "46-year-old male, knee surgery in Pune, 3-month-old insurance policy"

# Step 2: Convert query to vector using Hugging Face model
query_embedding = model.encode([query])  # Output is shape (1, 384)

# Step 3: Search top similar clause from FAISS
top_k = 5  # number of top similar clauses to retrieve
distances, indices = index.search(np.array(query_embedding), top_k)
matched_clauses = []
# Step 4: Show result
print("🔍 Best matching clause:")
for i in indices[0]:
    matched_clauses.append(clause[i])



# Step 3: Send to API
api_url = "http://localhost:8000/predict"
payload = {
    "user_query": user_query,
    "matched_clause": matched_clauses
}

response = requests.post(api_url, json=payload)
print("API Response:")
print(response.json())
