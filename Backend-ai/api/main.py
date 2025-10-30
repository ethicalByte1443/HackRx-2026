from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
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
import spacy
import re as re
from docx import Document
from fastapi.concurrency import run_in_threadpool


from spacy.cli import download


# ---------- Setup ----------


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


# Ensure the model is available
# ✅ Safe deployment version
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None          # graceful fallback – no hard download during boot

model = SentenceTransformer("all-MiniLM-L6-v2")



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

def parse_and_enhance_query(user_query):
    doc = nlp(user_query)
    keywords = []
    
    # Extract proper nouns, nouns, medical terms, numbers, locations, dates
    for token in doc:
        if token.ent_type_ in ['DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL']:
            keywords.append(token.text)
        elif token.ent_type_ in ['GPE', 'LOC']:
            keywords.append(token.text)
        elif token.pos_ in ['NOUN', 'PROPN', 'ADJ']:
            keywords.append(token.lemma_)  # Lemmatize to improve match
    
    # Join enhanced query
    enhanced_query = " ".join(keywords)
    
    return enhanced_query if enhanced_query else user_query



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
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                    "role": "user",
                    "content": prompt
                    }
                ],
                "temperature": 0.3
            }
        )

        result = response.json()
        print(result)

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

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), user_query: str = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Step 1: Save uploaded PDF
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Step 2: Run heavy logic in a background thread to prevent blocking
    def process_pdf():
        text = extract_text_from_pdf(file_path)
        real_clauses = extract_clauses_from_pdf(text)
        if not real_clauses:
            raise HTTPException(status_code=400, detail="No valid clauses found in PDF.")

        # Create FAISS index and embeddings
        clause_embeddings = model.encode(real_clauses)
        clause_embeddings_np = np.array(clause_embeddings)
        dimension = clause_embeddings_np.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(clause_embeddings_np)

        # Search for relevant clauses
        parsed_query = parse_and_enhance_query(user_query)
        query_embedding = model.encode([parsed_query])
        distances, indices = index.search(np.array(query_embedding), 5)
        matched_clauses = [real_clauses[i] for i in indices[0]]

        top_clauses = ', '.join(matched_clauses[:5])
        llm_result = process_claim(user_query, top_clauses)

        return {
            "matched_clauses": matched_clauses,
            "LLM_response": llm_result
        }

    # Run in a separate thread
    result = await run_in_threadpool(process_pdf)

    return {
        "message": "File uploaded and processed successfully.",
        "user_query": user_query,
        "matched_clauses": result["matched_clauses"],
        "LLM_response": result["LLM_response"]
    }


@app.post("/upload-docs")
async def upload_doc(file: UploadFile = File(...), user_query: str = Form(...)):
    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extract text from DOCX
    try:
        document = Document(file_path)
        text = "\n".join([para.text for para in document.paragraphs])
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to read Word document.")

    # Clause extraction
    real_clauses = extract_clauses_from_pdf(text)  # You can rename this to extract_clauses_from_doc if needed

    if not real_clauses:
        raise HTTPException(status_code=400, detail="No valid clauses found in Word document.")

    # Encode clauses
    clause_embeddings = model.encode(real_clauses)
    clause_embeddings_np = np.array(clause_embeddings).astype("float32")
    dimension = clause_embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(clause_embeddings_np)

    # Query embedding
    parsed_query = parse_and_enhance_query(user_query)
    print("Parsed Query:", parsed_query)
    query_embedding = model.encode([parsed_query])
    distances, indices = index.search(np.array(query_embedding), 5)

    # Matched clauses
    matched_clauses = [real_clauses[i] for i in indices[0]]
    top_clauses = ', '.join(matched_clauses[:5])

    # LLM processing
    result = process_claim(user_query, top_clauses)
    print(result)

    return {
        "message": "Word document uploaded and processed successfully.",
        "user_query": user_query,
        "matched_clauses": matched_clauses,
        "LLM_response": result
    }