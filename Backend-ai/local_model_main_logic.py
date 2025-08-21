# from transformers import AutoTokenizer, AutoModelForCausalLM
# import torch
# import json

# # Load Gemma 2B model and tokenizer
# tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b")
# model = AutoModelForCausalLM.from_pretrained(
#     "google/gemma-2b",
#     torch_dtype=torch.float16,
#     device_map="auto"
# )

# def process_claim(user_query, clause):
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
#         inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
#         outputs = model.generate(**inputs, max_new_tokens=200)
#         decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
#         # Extract only the JSON part after "Response:"
#         response_text = decoded.split("Response:")[-1].strip()

#         # Try parsing JSON if possible
#         json_start = response_text.find("{")
#         json_end = response_text.rfind("}") + 1
#         if json_start != -1 and json_end != -1:
#             json_data = response_text[json_start:json_end]
#             return json.loads(json_data)
#         else:
#             return {"error": "Could not parse JSON from response", "raw": response_text}
    
#     except Exception as e:
#         return {"error": str(e)}
