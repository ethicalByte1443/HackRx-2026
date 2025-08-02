# 🛡️ Insurance AI Agent

An intelligent insurance claim decision-making system built using **FastAPI** and **Hugging Face Transformers**. This AI agent analyzes insurance clauses and customer queries to predict whether a claim should be **Approved** or **Rejected**, along with a justification and estimated amount.

---

## 🚀 Features

- ✨ Uses **Gemma 1B/2B** large language model locally.
- 📑 Parses PDF policy documents using `PyMuPDF`.
- 🤖 Uses NLP to analyze **user queries** against **insurance clauses**.
- 🔥 Supports both **local inference** and **Hugging Face Inference API** (with/without API key).
- ⚡ Fast API backend with a clean REST endpoint `/predict`.

---

## 🧠 How It Works

1. **PDF Parsing**: 
   - The insurance policy document (`policy_clause.pdf`) is parsed using `PyMuPDF`.
   - Extracted text (clause) is used as reference to analyze claims.

2. **User Query Input**:
   - A user provides a natural language query like:
     > "I underwent surgery after 14 months of policy."

3. **LLM Inference**:
   - The query and clause are sent to a preloaded **Gemma 1B model**.
   - The model returns a **JSON output**:
     ```json
     {
       "decision": "Approved",
       "amount": "₹50,000",
       "justification": "The policy covers surgery after 12 months, and this claim is valid."
     }
     ```

4. **API Interface**:
   - The `/predict` route handles inference.
   - Users can send JSON input and get structured claim results.

---

## 🧪 Example Usage

### Input:
```json
{
  "user_query": "I was hospitalized 10 months after starting the policy.",
  "matched_clause": "Policy allows hospitalization claims only after 12 months of continuous coverage."
}
````

### Output:

```json
{
  "result": {
    "decision": "Rejected",
    "amount": "N/A",
    "justification": "Hospitalization occurred before the 12-month waiting period."
  }
}
```

---

## 🧰 Requirements

Install Python packages using:

```bash
pip install -r requirements.txt
```

### `requirements.txt` content:

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
huggingface_hub==0.19.0
transformers==4.35.0
torch==2.1.0
```

### For GPU users (CUDA 12.1):

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### For CPU-only users:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

---

## ⚙️ Running the API Locally

```bash
uvicorn main:app --reload
```

Visit: `http://localhost:8000/docs` to test the API with Swagger UI.

---

## 💡 Model Notes

* **Model Used:** `google/gemma-1.1-1b` or `google/gemma-2b`
* **Tokenizer:** Hugging Face `AutoTokenizer`
* **Local Inference:** No internet/API key needed
* **API Key Option:** You can alternatively use `InferenceClient` from `huggingface_hub` to query hosted models with an API key (less recommended for production).

---

## 📂 Project Structure

```
insurance-ai-agent/
├── main.py            # FastAPI backend
├── logic.py           # Claim processing logic
├── requirements.txt   # All dependencies
├── policy_clause.pdf  # Sample insurance policy
└── README.md
```

---

## 🧾 License

MIT License. Feel free to modify and use in your projects.

