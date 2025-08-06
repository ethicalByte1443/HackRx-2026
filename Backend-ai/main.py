from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import shutil
import fitz  # PyMuPDF
import numpy as np
import faiss
import json
import requests
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
import re as re

model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------- Setup ----------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

app = FastAPI()
UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# ---------- Utilities ----------
def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_clauses_from_pdf(text: str) -> list[str]:
    # hello
    text2 = text
    # Step 1: Normalize whitespace across the entire text
    cleaned_text = re.sub(r'\s+', ' ', text).strip()

    # Step 2: Split into clauses and clean again
    clauses = [
        clause.strip()
        for clause in cleaned_text.split(".")
        if len(clause.strip()) > 20
    ]

    return clauses

def get_fake_embedding(text: str):
    """Fake embedding just for testing — Groq doesn't provide embedding API."""
    return np.random.rand(384).tolist()

def get_fake_embeddings(texts: list[str]):
    return [get_fake_embedding(t) for t in texts]

def search_top_k_clauses(query: str, faiss_index, clauses, k=5):
    query_vector = np.array(get_fake_embedding(query)).reshape(1, -1)
    distances, indices = faiss_index.search(query_vector, k)
    return [clauses[i] for i in indices[0]]


def parse_and_enhance_query(user_query):
    # Simple keyword extraction using regex (no spaCy needed)
    # Remove common stop words and extract meaningful terms
    stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'as', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'to', 'of', 'in', 'for', 'with', 'by', 'from', 'and', 'or', 'but', 'not', 'no', 'so', 'if', 'then', 'than', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
    
    # Extract words and filter out stop words
    words = re.findall(r'\b[A-Za-z]{3,}\b', user_query.lower())
    keywords = [word for word in words if word not in stop_words]
    
    # Also extract numbers, dates, and monetary amounts
    numbers = re.findall(r'\b\d+(?:[.,]\d+)?\b', user_query)
    money_patterns = re.findall(r'[₹$€£]\s*\d+(?:[.,]\d+)?(?:\s*(?:lakh|crore|thousand|million|billion))?', user_query, re.IGNORECASE)
    
    # Combine all extracted terms
    all_terms = keywords + numbers + money_patterns
    
    return " ".join(all_terms) if all_terms else user_query

def process_claim(user_query: str, clause: str):
    prompt = f"""
You are an insurance claim analyst. Based on the user query and clause, decide the claim outcome.

Query: {user_query}

Clause: {clause}

Analyze if the claim should be approved or rejected based on the clause conditions. Return only a JSON response with these exact fields:
- decision: "Approved" or "Rejected"
- amount: estimated amount like "₹50000" or "N/A" if rejected
- justification: brief explanation based on the clause

Response:
"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",  # ✅ Use the updated model
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
        )

        result = response.json()

        if "choices" not in result or not result["choices"]:
            return {"error": "Unexpected response from Groq", "raw": result}

        content = result["choices"][0]["message"]["content"]
        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        if json_start != -1 and json_end != -1:
            return json.loads(content[json_start:json_end])
        return {"error": "Could not parse JSON", "raw": content}

    except Exception as e:
        return {"error": str(e)}
    
    
# ---------- Routes ----------
@app.get("/")
def root():
    return {"message": "Insurance Claim API running with Groq API for LLM."}

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": True}

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), user_query: str = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text_from_pdf(file_path)
    real_clauses = extract_clauses_from_pdf(text)

    if not real_clauses:
        raise HTTPException(status_code=400, detail="No valid clauses found in PDF.")

    clause_embeddings = model.encode(real_clauses)
    clause_embeddings_np = np.array(clause_embeddings)
    dimension = clause_embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(clause_embeddings_np)

    parsed_query = parse_and_enhance_query(user_query)
    print("Parsed Query:", parsed_query)

    # Step 2: Generate embedding and search
    query_embedding = model.encode([parsed_query])
    distances, indices = index.search(np.array(query_embedding), 5)

    # Step 3: Return matched clauses
    matched_clauses = [real_clauses[i] for i in indices[0]]

    top_clauses = ', '.join(matched_clauses[:5])
    payload = {
        "user_query": user_query,
        "matched_clause": top_clauses
    }


    result = process_claim(user_query, top_clauses)
    print(result)
    return {
        "message": "File uploaded and processed successfully.",
        "user_query": user_query,
        "matched_clauses": matched_clauses,
        "LLM_response": result
    }