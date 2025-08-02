from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from logic import process_claim

app = FastAPI()

class QueryData(BaseModel):
    user_query: str
    matched_clause: str

@app.get("/")
def root():
    return {"message": "Insurance Claim API running locally with Gemma 2B"}

@app.post("/predict")
def predict(data: QueryData):
    try:
        result = process_claim(data.user_query, data.matched_clause)
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(status_code=500, detail=result)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
