# utils.py
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def classify_document(text, pii_flags):
    """Use Gemini API to classify document sensitivity."""

    model = genai.GenerativeModel("gemini-flash-latest")

    prompt = f"""
You are a compliance and document-classification expert.

Classify this document into one or more of these categories:
1. Highly Sensitive: Content that includes PII like SSNs, account/credit card numbers, and proprietary schematics (e.g., defense or next‑gen product designs of military equipment).
2. Confidential: Internal communications and business documents, customer details (names, addresses), and non-public operational content.
3. Public: Marketing materials, product brochures, public website content, generic images.
4. Unsafe Content: Content must be evaluated for child safety and should not include hate speech, exploitative, violent, criminal, political news, or cyber-threat content.

Please also provide the confidence of your decision as a number between 0 and 1.

Here are some test cases for correctness:
🧪 Test Cases (for Judging & Testing)
🟢 TC1 — Public Marketing Document
Input: Multi-page brochure or program viewbook (Public) Expected Category: Public 

🔴 TC2 — Filled In Employment Application (PII)
Input: Application form containing synthetic PII (name, address, SSN) Expected Category: Highly Sensitive

🟡 TC3 — Internal Memo (No PII)
Input: Internal project memo with milestones/risks; no PII Expected Category: Confidential

✈️ TC4 — Stealth Fighter with Part Names
Input: High-resolution image of stealth fighter Expected Category: Confidential 

⚠️ TC5 — Testing Multiple Non-Compliance Categorizations
Input: Document embedded with a stealth fighter and unsafe content Expected Category: Confidential and Unsafe

Detected PII flags: {pii_flags}

Document text:
{text}

Respond with a short JSON object:
{{"category": "<one of the four>", "reason": "<brief explanation>"}}
"""

    response = model.generate_content(prompt)
    return response.text 
