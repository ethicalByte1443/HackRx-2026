import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import aiohttp
from pdfminer.high_level import extract_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set")


class HackRxRequest(BaseModel):
    documents: str  # URL to PDF
    questions: List[str]


class HackRxResponse(BaseModel):
    answers: List[str]  # Changed from Dict to List


@app.get("/health")
async def health():
    return {"status": "OK", "service": "HackRx Policy QA", "version": "1.0.0"}


@app.post("/hackrx/run", response_model=HackRxResponse, dependencies=[Depends(lambda: True)])
async def hackrx_run(req: HackRxRequest) -> HackRxResponse:
    temp_file = os.path.join(UPLOAD_DIR, "temp_policy.pdf")

    # Download PDF asynchronously
    async with aiohttp.ClientSession() as session:
        resp = await session.get(req.documents)
        if resp.status != 200:
            raise HTTPException(status_code=400, detail="Failed to download PDF")
        content = await resp.read()
        with open(temp_file, "wb") as f:
            f.write(content)

    # Extract text and split into clauses
    text = extract_text(temp_file) or ""
    clauses = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
    if not clauses:
        clauses = [p.strip() for p in text.split('. ') if len(p.strip()) > 50]
    # Limit clauses for performance
    clauses = clauses[:200]

    vectorizer = TfidfVectorizer(stop_words='english')

    answers = []

    for question in req.questions:
        best_score = 0
        best_clause = ""
        for clause in clauses:
            try:
                tfidf = vectorizer.fit_transform([question.lower(), clause.lower()])
                score = cosine_similarity(tfidf[0:1], tfidf[1:2]).flatten()[0]
            except Exception:
                score = 0
            if score > best_score:
                best_score = score
                best_clause = clause

        if not best_clause:
            answers.append("The policy does not provide information on this.")
            continue

        # Improved prompt to get concise, factual answers like your example
        prompt = f"""
You are an expert insurance assistant with deep knowledge of health insurance policies.

Given the question and the relevant policy excerpt below, provide a **short, direct, and precise** answer suitable for an official policy FAQ.

- Do NOT add disclaimers, repetitions, or hedging.
- If the information is missing, respond exactly: "The policy does not provide information on this."
- Quote or paraphrase key policy details clearly and concisely.

Question:
{question}

Policy Clause Excerpt:
{best_clause[:1500]}

Answer:
"""


        try:
            response = requests.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama3-8b-8192",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 800,
                },
                timeout=30,
            )
            result = response.json()
            if "choices" in result and result["choices"]:
                answer_text = result["choices"][0]["message"]["content"].strip()
                answers.append(answer_text)
            else:
                answers.append("The policy does not provide information on this.")
        except Exception as e:
            answers.append(f"Error from LLM: {str(e)}")

    # Clean up temp file
    if os.path.exists(temp_file):
        os.remove(temp_file)

    return HackRxResponse(answers=answers)
