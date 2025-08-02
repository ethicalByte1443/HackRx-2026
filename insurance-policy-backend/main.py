from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from logic import process_claim, process_claim_alternative, manual_claim_analysis
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Insurance Claim API",
    description="API for processing insurance claims using AI",
    version="1.0.0"
)

# Define the input data model
class QueryData(BaseModel):
    user_query: str
    matched_clause: str

# Root route to verify API is working
@app.get("/")
def root():
    return {
        "message": "Insurance Claim API is running with Flan-T5 backend.",
        "status": "healthy",
        "endpoints": ["/predict", "/predict-alternative", "/predict-manual", "/health"]
    }

# Health check route
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "insurance-claim-api"}

# Main prediction route
@app.post("/predict")
def predict(data: QueryData):
    try:
        # Validate input data
        if not data.user_query.strip():
            raise HTTPException(status_code=400, detail="user_query cannot be empty")
        
        if not data.matched_clause.strip():
            raise HTTPException(status_code=400, detail="matched_clause cannot be empty")
        
        print(f"Processing request:")
        print(f"User Query: {data.user_query}")
        print(f"Clause: {data.matched_clause}")
        
        # Process the claim
        result = process_claim(data.user_query, data.matched_clause)
        
        print(f"Processing result: {result}")
        
        # Return structured response
        return {
            "status": "success",
            "result": result,
            "input": {
                "user_query": data.user_query,
                "matched_clause": data.matched_clause
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Unexpected error in predict endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

# Alternative prediction route using transformers
@app.post("/predict-alternative")
def predict_alternative(data: QueryData):
    """Alternative endpoint using transformers pipeline"""
    try:
        if not data.user_query.strip():
            raise HTTPException(status_code=400, detail="user_query cannot be empty")
        
        if not data.matched_clause.strip():
            raise HTTPException(status_code=400, detail="matched_clause cannot be empty")
        
        result = process_claim_alternative(data.user_query, data.matched_clause)
        
        return {
            "status": "success",
            "result": result,
            "method": "transformers_pipeline",
            "input": {
                "user_query": data.user_query,
                "matched_clause": data.matched_clause
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Manual analysis route (fallback)
@app.post("/predict-manual")
def predict_manual(data: QueryData):
    """Manual rule-based analysis endpoint"""
    try:
        if not data.user_query.strip():
            raise HTTPException(status_code=400, detail="user_query cannot be empty")
        
        if not data.matched_clause.strip():
            raise HTTPException(status_code=400, detail="matched_clause cannot be empty")
        
        result = manual_claim_analysis(data.user_query, data.matched_clause, "Manual analysis requested")
        
        return {
            "status": "success",
            "result": result,
            "method": "manual_analysis",
            "input": {
                "user_query": data.user_query,
                "matched_clause": data.matched_clause
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Test endpoint


# Run the app
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
