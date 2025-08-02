from huggingface_hub import InferenceClient
import traceback
import json
import re

# Use flan-t5 model
client = InferenceClient(model="google/flan-t5-large")

def process_claim(user_query, clause):
    prompt = f"""
You are an insurance claim analyst. Based on the user query and clause, decide the claim outcome.

Query: {user_query}

Clause: {clause}

Analyze if the claim should be approved or rejected based on the clause conditions. Return only a JSON response with these exact fields:
- decision: "Approved" or "Rejected"
- amount: estimated amount like "₹50000" or "N/A" if rejected
- justification: brief explanation based on the clause

Response:"""
    
    try:
        print("Processing claim...")
        print(f"Prompt: {prompt[:200]}...")
        
        # CORRECT method - use text_generation() directly (not client.text_generation)
        result = client.text_generation(
            prompt,
            max_new_tokens=200,
            temperature=0.1,
            do_sample=True,
            return_full_text=False
        )
        
        print(f"Raw result: {result}")
        
        # Clean and parse the result
        cleaned_result = clean_and_parse_response(result)
        return cleaned_result
        
    except Exception as e:
        print("Error occurred:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        traceback.print_exc()
        
        # Return a fallback response with manual analysis
        return manual_claim_analysis(user_query, clause, str(e))

def manual_claim_analysis(user_query, clause, error_msg):
    """Fallback manual analysis when API fails"""
    try:
        query_lower = user_query.lower()
        clause_lower = clause.lower()
        
        # Extract key information
        decision = "Rejected"
        amount = "N/A"
        justification = f"Manual analysis due to API error: {error_msg[:100]}"
        
        # Simple rule-based analysis
        if "surgery" in query_lower and "covered" in clause_lower:
            # Check time conditions
            if "month" in clause_lower and "month" in query_lower:
                # Extract numbers from both strings
                clause_months = re.findall(r'(\d+).*month', clause_lower)
                query_months = re.findall(r'(\d+).*month', query_lower)
                
                if clause_months and query_months:
                    required_months = int(clause_months[0])
                    actual_months = int(query_months[0])
                    
                    if actual_months >= required_months:
                        decision = "Approved"
                        amount = "₹75000"  # Default surgery amount
                        justification = f"Policy active for {actual_months} months, meets {required_months} month requirement for surgery coverage"
                    else:
                        justification = f"Policy active for only {actual_months} months, requires {required_months} months for surgery coverage"
        
        return {
            "decision": decision,
            "amount": amount,
            "justification": justification,
            "fallback": True
        }
    except Exception as fallback_error:
        return {
            "decision": "Error",
            "amount": "N/A",
            "justification": f"Both API and fallback failed: {str(fallback_error)}",
            "error": True
        }

def clean_and_parse_response(raw_response):
    """Clean and parse the model response to extract JSON"""
    try:
        # Handle different response types
        if hasattr(raw_response, 'generated_text'):
            response_text = raw_response.generated_text
        elif isinstance(raw_response, str):
            response_text = raw_response
        else:
            response_text = str(raw_response)
        
        print(f"Cleaning response: {response_text}")
        
        # Try to find JSON-like content
        json_match = re.search(r'\{[^}]*\}', response_text)
        if json_match:
            json_str = json_match.group()
            try:
                parsed_json = json.loads(json_str)
                # Validate required fields
                if all(key in parsed_json for key in ['decision', 'amount', 'justification']):
                    return parsed_json
            except json.JSONDecodeError:
                pass
        
        # If no valid JSON found, create structured response from text
        decision = "Rejected"
        amount = "N/A"
        justification = response_text.strip()
        
        # Simple logic to determine approval
        if any(word in response_text.lower() for word in ["approved", "approve", "covered", "eligible"]):
            decision = "Approved"
            # Try to extract amount if mentioned
            amount_match = re.search(r'₹[\d,]+', response_text)
            if amount_match:
                amount = amount_match.group()
            else:
                amount = "₹50000"  # Default amount for approved claims
        
        return {
            "decision": decision,
            "amount": amount,
            "justification": justification[:200]  # Limit length
        }
        
    except Exception as e:
        print(f"Error in cleaning response: {str(e)}")
        return {
            "decision": "Error",
            "amount": "N/A",
            "justification": f"Response parsing error: {str(e)}"
        }

# Alternative using transformers pipeline (more reliable for local use)
def process_claim_alternative(user_query, clause):
    """Alternative method using transformers pipeline"""
    try:
        from transformers import pipeline
        
        # Initialize pipeline
        pipe = pipeline("text2text-generation", model="google/flan-t5-base")  # Using base model
        
        prompt = f"Analyze insurance claim: Query: {user_query}. Clause: {clause}. Should this be approved or rejected and why?"
        
        result = pipe(prompt, max_length=150, temperature=0.3)
        response_text = result[0]['generated_text']
        
        # Determine decision based on response
        decision = "Approved" if any(word in response_text.lower() for word in ["approved", "approve", "covered"]) else "Rejected"
        amount = "₹50000" if decision == "Approved" else "N/A"
        
        return {
            "decision": decision,
            "amount": amount,
            "justification": response_text,
            "method": "transformers_pipeline"
        }
    except ImportError:
        return {
            "decision": "Error",
            "amount": "N/A",
            "justification": "Transformers library not available",
            "error": True
        }
    except Exception as e:
        return {
            "decision": "Error",
            "amount": "N/A",
            "justification": f"Pipeline error: {str(e)}",
            "error": True
        }
