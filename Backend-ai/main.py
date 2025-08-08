from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv
import os
import re
import fitz  # PyMuPDF
import json
import requests
import aiohttp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------- Setup ----------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Bearer token for hackathon
TEAM_TOKEN = "ca7c5627922a58ccf3887ccb9c81e59655363400372cb9b33c7dac74e3c5473b"
auth_scheme = HTTPBearer()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- TF-IDF Setup ----------
vectorizer = TfidfVectorizer(
    max_features=500,
    stop_words='english',
    max_df=0.95,
    min_df=1,
    ngram_range=(1, 2)
)

# ---------- Authentication ----------
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if credentials.credentials != TEAM_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

# ---------- Models ----------
class HackRxRequest(BaseModel):
    documents: HttpUrl
    questions: list[str]

# ---------- Utils ----------
def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_clauses_from_pdf(text: str) -> list[str]:
    if len(text) > 50000:
        text = text[:50000] + "..."

    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    clauses = []

    # By periods
    for clause in cleaned_text.split("."):
        clause = clause.strip()
        if 30 < len(clause) < 1000:
            clauses.append(clause)

    # Numbered clauses
    numbered_pattern = r'(?:^|\n)\s*\d+\.\s*([^.]+(?:\.[^.]*)*)'
    numbered_matches = re.findall(numbered_pattern, text, re.MULTILINE)
    for match in numbered_matches:
        if 30 < len(match) < 1000:
            clauses.append(match.strip())

    return list(set(clauses))[:100]

def parse_and_enhance_query(user_query):
    stop_words = {
        'the', 'is', 'at', 'which', 'on', 'a', 'an', 'as', 'are', 'was', 'were',
        'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can', 'to', 'of', 'in', 'for',
        'with', 'by', 'from', 'and', 'or', 'but', 'not', 'no', 'so', 'if', 'then',
        'than', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
        'we', 'they', 'me', 'him', 'her', 'us', 'them'
    }
    words = re.findall(r'\b[A-Za-z]{3,}\b', user_query.lower())
    keywords = [word for word in words if word not in stop_words]
    numbers = re.findall(r'\b\d+(?:[.,]\d+)?\b', user_query)
    money_patterns = re.findall(r'[₹$€£]\s*\d+(?:[.,]\d+)?(?:\s*(?:lakh|crore|thousand|million|billion))?', user_query, re.IGNORECASE)
    return " ".join(keywords + numbers + money_patterns) or user_query

def find_relevant_clauses(query: str, clauses: list[str], top_k: int = 5):
    if not clauses:
        return []

    if len(clauses) > 50:
        clauses = clauses[:50]

    all_texts = [query] + clauses
    try:
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        query_vector = tfidf_matrix[0:1]
        clause_vectors = tfidf_matrix[1:]
        similarities = cosine_similarity(query_vector, clause_vectors).flatten()
        top_indices = similarities.argsort()[-top_k:][::-1]
        return [clauses[i] for i in top_indices if similarities[i] > 0.05]
    except:
        return clauses[:top_k]

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
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }
        )
        result = response.json()
        if "choices" not in result or not result["choices"]:
            return {"justification": "No valid response from LLM"}
        content = result["choices"][0]["message"]["content"]
        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        if json_start != -1 and json_end != -1:
            return json.loads(content[json_start:json_end])
        return {"justification": "LLM failed to produce JSON"}
    except Exception as e:
        return {"justification": f"LLM Error: {str(e)}"}

# ---------- Main HackRx Endpoint ----------
@app.post("/hackrx/run", dependencies=[Depends(verify_token)])
async def hackrx_run(request: HackRxRequest):
    pdf_url = request.documents
    questions = request.questions

    temp_file_path = os.path.join(UPLOAD_DIR, "temp_policy.pdf")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=400, detail="Failed to download the PDF.")
                content = await response.read()
                if not isinstance(content, bytes):
                    raise HTTPException(status_code=400, detail="Invalid content received.")
                with open(temp_file_path, "wb") as f:
                    f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF download error: {str(e)}")

    text = extract_text_from_pdf(temp_file_path)
    real_clauses = extract_clauses_from_pdf(text)
    if not real_clauses:
        raise HTTPException(status_code=400, detail="No valid clauses found in document.")

    answers = []
    for question in questions:
        parsed_query = parse_and_enhance_query(question)
        matched_clauses = find_relevant_clauses(parsed_query, real_clauses, top_k=5)
        if not matched_clauses:
            matched_clauses = find_relevant_clauses(question, real_clauses, top_k=5)
        top_clauses = ', '.join(matched_clauses[:5])
        result = process_claim(question, top_clauses)
        if isinstance(result, dict) and "justification" in result:
            answers.append(result["justification"])
        else:
            answers.append("Unable to determine answer.")

    try:
        os.remove(temp_file_path)
    except:
        pass

    return {"answers": answers}

# ---------- Health Check ----------
@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": True}
