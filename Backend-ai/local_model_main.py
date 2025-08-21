# from fastapi import FastAPI, File, HTTPException, UploadFile, Form
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import os
# import shutil
# import fitz  # PyMuPDF
# import numpy as np
# import faiss
# import requests
# from sentence_transformers import SentenceTransformer
# from transformers import AutoTokenizer, AutoModelForCausalLM
# import torch
# import json

# # ---------- Setup ----------
# app = FastAPI()
# UPLOAD_DIR = "uploaded_pdfs"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:8080"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# model = SentenceTransformer("all-MiniLM-L6-v2")

# # Load Gemma 2B model and tokenizer
# tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b")
# lm_model = AutoModelForCausalLM.from_pretrained(
#     "google/gemma-2b",
#     torch_dtype=torch.float16,
#     device_map="auto"
# )

# # ---------- Utilities ----------

# def extract_text_from_pdf(file_path: str) -> str:
#     doc = fitz.open(file_path)
#     text = ""
#     for page in doc:
#         text += page.get_text()
#     doc.close()
#     print("extract_text_from_pdf CALLED -> text = ", text[0:100])
#     return text

# def extract_clauses_from_pdf(text: str) -> list[str]:
#     clauses = [clause.strip() for clause in text.split(".") if len(clause.strip()) > 20]
#     print("extract_clauses_from_pdf --> clauses --> ", clauses[0:10])
#     return clauses

# def search_top_k_clauses(query: str, model, faiss_index, clauses, k=5):
#     query_vector = model.encode([query])
#     distances, indices = faiss_index.search(np.array(query_vector), k)
#     return [clauses[i] for i in indices[0]]

# def process_claim(user_query, clause):
#     prompt = f"""
# You are an insurance claim analyst. Based on the user query and clause, decide the claim outcome.

# Query: {user_query}

# Clause: {clause}

# Analyze if the claim should be approved or rejected based on the clause conditions. Return only a JSON response with these exact fields:
# - decision: \"Approved\" or \"Rejected\"
# - amount: estimated amount like \"\u20b950000\" or \"N/A\" if rejected
# - justification: brief explanation based on the clause

# Response:
# """
#     try:
#         inputs = tokenizer(prompt, return_tensors="pt").to(lm_model.device)
#         outputs = lm_model.generate(**inputs, max_new_tokens=200)
#         decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
#         response_text = decoded.split("Response:")[-1].strip()

#         json_start = response_text.find("{")
#         json_end = response_text.rfind("}") + 1
#         if json_start != -1 and json_end != -1:
#             json_data = response_text[json_start:json_end]
#             return json.loads(json_data)
#         else:
#             return {"error": "Could not parse JSON from response", "raw": response_text}
#     except Exception as e:
#         return {"error": str(e)}

# # ---------- Routes ----------

# @app.get("/")
# def root():
#     return {"message": "Insurance Claim API running with real clause extraction and semantic search."}

# @app.post("/upload-pdf")
# async def upload_pdf(
#     file: UploadFile = File(...),
#     user_query: str = Form(...)
# ):
    
#     print("User_query is : ", user_query)
#     file_location = os.path.join(UPLOAD_DIR, file.filename)
#     with open(file_location, "wb") as f:
#         f.write(await file.read())

#     text = extract_text_from_pdf(file_location)
#     real_clauses = extract_clauses_from_pdf(text)

#     if not real_clauses:
#         raise HTTPException(status_code=400, detail="No valid clauses found in PDF.")

#     clause_embeddings = model.encode(real_clauses)
#     clause_embeddings_np = np.array(clause_embeddings)
#     dimension = clause_embeddings_np.shape[1]
#     index = faiss.IndexFlatL2(dimension)
#     index.add(clause_embeddings_np)

#     query_embedding = model.encode([user_query])
#     distances, indices = index.search(np.array(query_embedding), 5)
#     matched_clauses = [real_clauses[i] for i in indices[0]]

#     top_clauses = ', '.join(matched_clauses[:5])
#     payload = {
#         "user_query": user_query,
#         "matched_clause": top_clauses
#     }

#     result = process_claim(user_query, top_clauses)
#     print(result)
#     return {
#         "message": "File uploaded and processed successfully.",
#         "user_query": user_query,
#         "matched_clauses": matched_clauses,
#         "LLM_response": result
#     }

# @app.post("/match-query-from-upload")
# async def match_query_from_pdf(file: UploadFile = File(...), query: str = Form(...)):
#     file_location = os.path.join(UPLOAD_DIR, file.filename)
#     with open(file_location, "wb") as f:
#         f.write(await file.read())

#     text = extract_text_from_pdf(file_location)
#     real_clauses = extract_clauses_from_pdf(text)

#     if not real_clauses:
#         raise HTTPException(status_code=400, detail="No valid clauses found in PDF.")

#     clause_vectors = model.encode(real_clauses)
#     index = faiss.IndexFlatL2(clause_vectors.shape[1])
#     index.add(np.array(clause_vectors))

#     top_matches = search_top_k_clauses(query, model, index, real_clauses)

#     return {
#         "user_query": query,
#         "top_5_matched_clauses": top_matches
#     }

# @app.post("/test-query")
# def test_query():
#     dummy_clauses = [
#         "This policy covers accidental damage.",
#         "Third-party liabilities are not covered.",
#         "Notify insurer within 24 hours of incident.",
#         "Medical expenses are reimbursed up to \u20b91 lakh.",
#         "The claim must include a police report.",
#         "Intentional damage is not covered.",
#         "Only the primary policyholder can file a claim.",
#         "Pre-existing conditions are excluded.",
#         "Damage due to natural disasters is included.",
#         "Claim approval takes up to 15 working days."
#     ]
#     dummy_vectors = model.encode(dummy_clauses)
#     temp_index = faiss.IndexFlatL2(dummy_vectors.shape[1])
#     temp_index.add(np.array(dummy_vectors))

#     user_query = "Will the company pay for hospital bills after accident?"
#     top_matches = search_top_k_clauses(user_query, model, temp_index, dummy_clauses)

#     return {
#         "user_query": user_query,
#         "top_5_matched_clauses": top_matches
#     }

