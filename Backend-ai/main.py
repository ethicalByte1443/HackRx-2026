from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import shutil
import fitz  # PyMuPDF
import json
import requests
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
import re as re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Use lightweight TF-IDF instead of heavy sentence transformers
vectorizer = TfidfVectorizer(
    max_features=500,  # Reduced from 1000 to save memory
    stop_words='english',
    max_df=0.95,  # Ignore terms that appear in >95% of documents
    min_df=1,  # Include terms that appear in at least 1 document
    ngram_range=(1, 2)  # Include unigrams and bigrams
)

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
    # Memory-efficient clause extraction
    # Step 1: Normalize whitespace and limit text size
    if len(text) > 50000:  # Limit text to 50KB to save memory
        text = text[:50000] + "..."
    
    cleaned_text = re.sub(r'\s+', ' ', text).strip()

    # Step 2: Split into clauses using multiple delimiters
    # Split by periods, but also by numbered clauses
    clauses = []
    
    # First split by periods
    period_splits = cleaned_text.split(".")
    
    for clause in period_splits:
        clause = clause.strip()
        if len(clause) > 30 and len(clause) < 1000:  # Skip very short or very long clauses
            clauses.append(clause)
    
    # Also try to extract numbered clauses (1., 2., etc.)
    numbered_pattern = r'(?:^|\n)\s*\d+\.\s*([^.]+(?:\.[^.]*)*)'
    numbered_matches = re.findall(numbered_pattern, text, re.MULTILINE)
    
    for match in numbered_matches:
        if len(match) > 30 and len(match) < 1000:
            clauses.append(match.strip())
    
    # Remove duplicates and limit total clauses to save memory
    unique_clauses = list(set(clauses))
    return unique_clauses[:100]  # Limit to 100 clauses max

def find_relevant_clauses(query: str, clauses: list[str], top_k: int = 5):
    """Find most relevant clauses using TF-IDF similarity (lightweight)"""
    if not clauses:
        return []
    
    # Limit clauses to save memory
    if len(clauses) > 50:
        clauses = clauses[:50]
    
    # Combine query with clauses for vectorization
    all_texts = [query] + clauses
    
    try:
        # Create TF-IDF vectors
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        # Calculate cosine similarity between query and all clauses
        query_vector = tfidf_matrix[0:1]  # First row is the query
        clause_vectors = tfidf_matrix[1:]  # Rest are clauses
        
        similarities = cosine_similarity(query_vector, clause_vectors).flatten()
        
        # Get top k most similar clauses
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        result = [clauses[i] for i in top_indices if similarities[i] > 0.05]  # Lower threshold
        
        # Clean up
        del tfidf_matrix, query_vector, clause_vectors, similarities
        
        return result
    except Exception as e:
        print(f"TF-IDF error: {e}")
        # Fallback: simple keyword matching
        query_words = set(query.lower().split())
        scored_clauses = []
        for clause in clauses:
            clause_words = set(clause.lower().split())
            score = len(query_words.intersection(clause_words))
            if score > 0:
                scored_clauses.append((clause, score))
        
        # Sort by score and return top k
        scored_clauses.sort(key=lambda x: x[1], reverse=True)
        return [clause for clause, score in scored_clauses[:top_k]]


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

    # Use lightweight TF-IDF similarity instead of heavy embeddings
    parsed_query = parse_and_enhance_query(user_query)
    print("Parsed Query:", parsed_query)

    # Find relevant clauses using TF-IDF
    matched_clauses = find_relevant_clauses(parsed_query, real_clauses, top_k=5)

    if not matched_clauses:
        # Fallback: use original query if parsed query doesn't match
        matched_clauses = find_relevant_clauses(user_query, real_clauses, top_k=5)
    
    top_clauses = ', '.join(matched_clauses[:5])
    
    result = process_claim(user_query, top_clauses)
    print(result)
    
    # Clean up the uploaded file to save space
    try:
        os.remove(file_path)
    except:
        pass
    
    return {
        "message": "File uploaded and processed successfully.",
        "user_query": user_query,
        "matched_clauses": matched_clauses,
        "LLM_response": result
    }