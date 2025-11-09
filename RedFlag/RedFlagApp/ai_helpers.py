import os 
import requests
import json
#cohere helper
def call_cohere_api(context_package):
    url = "https://api.cohere.ai/v1/chat"
    headers = {
        "Authorization": f"Bearer {os.environ.get('COHERE_API_KEY')}",
        "Content-Type": "application/json"
    }
    responses = []
    for prompt in context_package["prompt_sequence"]:
        full_message = f"""
        Prompt: {prompt}
        Query: {context_package.get('query', '')}
        Document: {json.dumps(context_package['document'])}
        External Context: {json.dumps(context_package['external_context'])}"""      
        data = {"message": full_message, "model": "command", "temperature": 0.3}
        resp = requests.post(url, headers=headers, json=data, timeout = 20)
        resp.raise_for_status()
        result = resp.json().get("text", "")
        confidence = resp.json().get("confidence", 0.8)
        responses.append({"prompt": prompt, "response": result, "confidence": confidence})
    
    if responses:
        avg_confidence = sum(r.get("cnofidence", 0) for r in responses)/ len(responses)
        return {
            "responses": responses,
            "confidence": avg_confidence
        }
    return {"confidence": 0.0, "responses": []}

    

def call_gemini_api(context_package):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + os.environ.get('GOOGLE_API_KEY')
    responses = []
    for prompt in context_package["prompt_sequence"]:
        #building the content for gemini
        full_content = f"""
        Prompt: {prompt}
        Query: {context_package.get('query', '')}
        Document: {json.dumps(context_package['document'])}
        External Context: {json.dumps(context_package['external_context'])}

        Please provide a structured response.
        """
        data = {"contents": [{
            "parts":[{
                "text": full_content
            }]
        }], "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 3000,
        }}
        resp = requests.post(url,json=data, timeout=20)
        resp.raise_for_status()
        jdata = resp.json()
        result =""
        candidates = jdata.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                result = parts[0].get("text", "")
        confidence = jdata.get("safetyAttributes", {}).get("overallSafetyRating", 0.0)
        #placeholder- i dont really know what this means
        responses.append({"prompt": prompt, "response": result, "confidence": confidence})
    if responses:
        avg_confidence = sum(r.get("cnofidence", 0) for r in responses)/ len(responses)
        return {
            "responses": responses,
            "confidence": avg_confidence
        }
    return {"confidence": 0.0, "responses": []}
    
    
    