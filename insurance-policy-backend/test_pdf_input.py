import requests

payload = {
    "user_query": "I was hospitalized 10 months after starting the policy.",
    "matched_clause": "Policy allows hospitalization claims only after 12 months of continuous coverage."
}

res = requests.post("http://localhost:8000/predict", json=payload)
print(res.json())
