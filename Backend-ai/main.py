from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import aiohttp
import os
from pdfminer.high_level import extract_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Dummy token verification dependency
def verify_token():
    # implement your token verification here
    return True

class HackRxRequest(BaseModel):
    documents: str
    questions: List[str]

def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF extraction error: {str(e)}")

def extract_clauses_from_pdf(text: str) -> List[str]:
    # Split on double newlines or periods, customize as needed
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if not paragraphs:
        paragraphs = [p.strip() for p in text.split('. ') if p.strip()]
    return paragraphs

def parse_and_enhance_query(query: str) -> str:
    # Optionally add synonyms or clean query here
    return query.lower()

@app.get("/health")
async def health():
    return {
        "status": "OK",
        "service": "HackRx Policy Clauses",
        "version": "1.0.0"
    }

@app.post("/hackrx/run", dependencies=[Depends(verify_token)])
async def hackrx_run(request: HackRxRequest):
    pdf_url = request.documents
    questions = request.questions

    temp_file_path = os.path.join(UPLOAD_DIR, "temp_policy.pdf")
    # Download PDF
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(str(pdf_url)) as response:
                if response.status != 200:
                    raise HTTPException(status_code=400, detail="Failed to download the PDF.")
                content_type = response.headers.get('Content-Type', '').lower()
                if not ('pdf' in content_type or 'application/octet-stream' in content_type):
                    raise HTTPException(status_code=400, detail=f"URL did not return a PDF. Content-Type: {content_type}")
                content = await response.read()
                with open(temp_file_path, "wb") as f:
                    f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF download error: {str(e)}")

    # Extract text & clauses
    text = extract_text_from_pdf(temp_file_path)
    clauses = extract_clauses_from_pdf(text)
    if not clauses:
        raise HTTPException(status_code=400, detail="No valid clauses found in document.")

    vectorizer = TfidfVectorizer(stop_words='english')

    answers = []
    for question in questions:
        parsed_query = parse_and_enhance_query(question)
        best_score = 0.0
        best_clause = ""
        for clause in clauses:
            try:
                tfidf = vectorizer.fit_transform([parsed_query, clause.lower()])
                score = cosine_similarity(tfidf[0:1], tfidf[1:2]).flatten()[0]
            except Exception:
                score = 0.0
            if score > best_score:
                best_score = score
                best_clause = clause
        if best_clause:
            # Truncate to 1200 chars to avoid huge responses
            answers.append(best_clause.strip()[:1200])
        else:
            answers.append("No relevant information found.")

    # Clean up temp file
    try:
        os.remove(temp_file_path)
    except Exception:
        pass

    return {"answers": answers}

# from fastapi import FastAPI, HTTPException, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from pydantic import BaseModel, HttpUrl
# from dotenv import load_dotenv
# import os
# import re
# import fitz  # PyMuPDF
# import json
# import requests
# import aiohttp
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

# # ---------- Setup ----------
# load_dotenv()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# print(f"DEBUG: GROQ_API_KEY loaded: '{GROQ_API_KEY}'")
# GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
# UPLOAD_DIR = "uploaded_pdfs"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# TEAM_TOKEN = os.getenv("TEAM_TOKEN")
# auth_scheme = HTTPBearer()

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ---------- TF-IDF Setup ----------
# vectorizer = TfidfVectorizer(
#     max_features=500,
#     stop_words='english',
#     max_df=0.95,
#     min_df=1,
#     ngram_range=(1, 2)
# )

# # ---------- Authentication ----------
# def verify_token(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
#     expected_token = TEAM_TOKEN
#     if expected_token and expected_token.startswith("Bearer "):
#         expected_token = expected_token[len("Bearer "):]
#     print(f"DEBUG: Received token: '{credentials.credentials}'")
#     print(f"DEBUG: Expected token: '{expected_token}'")
#     if credentials.credentials != expected_token:
#         print(f"DEBUG: Token mismatch. Received: '{credentials.credentials}', Expected: '{expected_token}'")
#         raise HTTPException(status_code=401, detail="Unauthorized")

# # ---------- Models ----------
# class HackRxRequest(BaseModel):
#     documents: HttpUrl
#     questions: list[str]

# # ---------- Utils ----------
# def extract_text_from_pdf(file_path: str) -> str:
#     if not isinstance(file_path, str):
#         print(f"DEBUG: file_path is not a string: {file_path} (type: {type(file_path)})")
#         raise HTTPException(status_code=500, detail="Internal error: file path is not a string.")
#     if not os.path.isfile(file_path):
#         print(f"DEBUG: file does not exist at path: {file_path}")
#         raise HTTPException(status_code=500, detail=f"PDF file does not exist at path: {file_path}")
#     try:
#         print(f"DEBUG: Opening PDF at path: {file_path}")
#         doc = fitz.open(file_path)
#         text = ""
#         for page in doc:
#             text += page.get_text()
#         doc.close()
#         return text
#     except Exception as e:
#         print(f"DEBUG: Error opening PDF: {e}, file_path: {file_path}")
#         raise HTTPException(status_code=500, detail=f"PDF extraction error: {str(e)}")

# def extract_clauses_from_pdf(text: str) -> list[str]:
#     paragraphs = re.split(r'\n{2,}', text)
#     cleaned_paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 50]
#     return cleaned_paragraphs[:100]

# def parse_and_enhance_query(user_query: str) -> str:
#     stop_words = {
#         'the', 'is', 'at', 'which', 'on', 'a', 'an', 'as', 'are', 'was', 'were',
#         'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
#         'could', 'should', 'may', 'might', 'must', 'can', 'to', 'of', 'in', 'for',
#         'with', 'by', 'from', 'and', 'or', 'but', 'not', 'no', 'so', 'if', 'then',
#         'than', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
#         'we', 'they', 'me', 'him', 'her', 'us', 'them'
#     }
#     words = re.findall(r'\b[A-Za-z]{3,}\b', user_query.lower())
#     keywords = [word for word in words if word not in stop_words]
#     numbers = re.findall(r'\b\d+(?:[.,]\d+)?\b', user_query)
#     money_patterns = re.findall(r'[₹$€£]\s*\d+(?:[.,]\d+)?(?:\s*(?:lakh|crore|thousand|million|billion))?', user_query, re.IGNORECASE)
#     return " ".join(keywords + numbers + money_patterns) or user_query

# def find_relevant_clauses(query: str, clauses: list[str], top_k: int = 5) -> list[str]:
#     if not clauses:
#         return []

#     if len(clauses) > 50:
#         clauses = clauses[:50]

#     all_texts = [query] + clauses
#     try:
#         tfidf_matrix = vectorizer.fit_transform(all_texts)
#         query_vector = tfidf_matrix[0:1]
#         clause_vectors = tfidf_matrix[1:]
#         similarities = cosine_similarity(query_vector, clause_vectors).flatten()
#         top_indices = similarities.argsort()[-top_k:][::-1]
#         return [clauses[i] for i in top_indices if similarities[i] > 0.05]
#     except Exception as e:
#         print(f"DEBUG: Exception in find_relevant_clauses: {e}")
#         return clauses[:top_k]

# def process_claim(user_query: str, clause: str):
#     prompt = f"""
# You are an insurance claim analyst. Based on the user query and clause, decide the claim outcome.

# Query: {user_query}
# Clause: {clause}

# Analyze if the claim should be approved or rejected based on the clause conditions. Return only a JSON response with these exact fields:
# - decision: "Approved" or "Rejected"
# - amount: estimated amount like "₹50000" or "N/A" if rejected
# - justification: brief explanation based on the clause

# Response:
# """
#     try:
#         response = requests.post(
#             GROQ_API_URL,
#             headers={
#                 "Authorization": f"Bearer {GROQ_API_KEY}",
#                 "Content-Type": "application/json",
#             },
#             json={
#                 "model": "llama-3.3-70b-versatile",
#                 "messages": [{"role": "user", "content": prompt}],
#                 "temperature": 0.3
#             }
#         )
#         print(f"DEBUG: Groq API response status: {response.status_code}")
#         print(f"DEBUG: Groq API response text: {response.text}")
#         result = response.json()
#         if "choices" not in result or not result["choices"]:
#             return {"decision": "Rejected", "amount": "N/A", "justification": "No valid response from LLM"}
#         content = result["choices"][0]["message"]["content"]
#         json_start = content.find("{")
#         json_end = content.rfind("}") + 1
#         if json_start != -1 and json_end != -1:
#             try:
#                 parsed = json.loads(content[json_start:json_end])
#                 return parsed
#             except Exception as e:
#                 print(f"DEBUG: JSON parse error: {e}, content: {content}")
#                 return {"decision": "Rejected", "amount": "N/A", "justification": "LLM response not valid JSON"}
#         return {"decision": "Rejected", "amount": "N/A", "justification": "LLM failed to produce JSON"}
#     except Exception as e:
#         print(f"DEBUG: Exception in Groq API call: {e}")
#         return {"decision": "Rejected", "amount": "N/A", "justification": f"LLM Error: {str(e)}"}

# # ---------- Main HackRx Endpoint ----------
# @app.post("/hackrx/run", dependencies=[Depends(verify_token)])
# async def hackrx_run(request: HackRxRequest):
#     pdf_url = request.documents
#     questions = request.questions

#     temp_file_path = os.path.join(UPLOAD_DIR, "temp_policy.pdf")
#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.get(str(pdf_url)) as response:
#                 if response.status != 200:
#                     raise HTTPException(status_code=400, detail="Failed to download the PDF.")
#                 content_type = response.headers.get('Content-Type', '').lower()
#                 if not ('pdf' in content_type or 'application/octet-stream' in content_type):
#                     raise HTTPException(status_code=400, detail=f"URL did not return a PDF. Content-Type: {content_type}")
#                 with open(temp_file_path, "wb") as f:
#                     f.write(await response.read())
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"PDF download error: {str(e)}")

#     text = extract_text_from_pdf(temp_file_path)
#     real_clauses = extract_clauses_from_pdf(text)
#     if not real_clauses:
#         raise HTTPException(status_code=400, detail="No valid clauses found in document.")

#     answers = []
#     for question in questions:
#         parsed_query = parse_and_enhance_query(question)
#         best_score = 0.0
#         best_para = ""
#         for para in real_clauses:
#             sentences = re.split(r'(?<=[.!?])\s+', para)
#             for sent in sentences:
#                 try:
#                     tfidf_matrix = vectorizer.fit_transform([parsed_query, sent])
#                     score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()[0]
#                 except Exception:
#                     score = 0.0
#                 if score > best_score:
#                     best_score = score
#                     best_para = para
#         context = best_para[:1200] if best_para else (real_clauses[0][:1200] if real_clauses else "")
#         result = process_claim(question, context)
#         answers.append(result)

#     try:
#         os.remove(temp_file_path)
#     except Exception:
#         pass

#     return {"answers": answers}

# # ---------- Health Check ----------
# @app.get("/health")
# def health_check():
#     return {"status": "healthy", "model_loaded": True}
