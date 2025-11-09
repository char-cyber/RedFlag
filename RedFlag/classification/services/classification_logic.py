# utils.py
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def classify_document(text, pii_flags, given_page_num, given_image_num):
    """Use Gemini API to classify document sensitivity."""

    model = genai.GenerativeModel("gemini-flash-latest")

    prompt = f"""
You are a compliance and document-classification expert.

Classify this document into one or more of these categories:
1. Highly Sensitive: Content that includes PII like SSNs, account/credit card numbers, and proprietary schematics (e.g., defense or next‑gen product designs of military equipment).
2. Confidential: Internal communications and business documents, customer details (names, addresses), and non-public operational content.
3. Public: Marketing materials, product brochures, public website content, generic images.
4. Unsafe Content: Content must be evaluated for child safety and should not include hate speech, exploitative, violent, criminal, political news, or cyber-threat content.



Also, determine if any of the following flags are present:
1. Proprietary schematics / technical designs: Defense systems, next-gen products, or blueprints.
2. Internal communications: Emails, memos, or chat transcripts not meant for external sharing.
3. Business strategic documents: Plans, budgets, forecasts, or corporate strategies.
4. Research & development materials: Experimental designs, lab results, prototypes.
5. Customer data / PII: Names, addresses, account information, or sensitive personal data.
6. Legal agreements / contracts: NDAs, licensing agreements, or partnership contracts.
7. Pricing and financial strategies: Cost models, discount structures, competitor analyses.
8. Executive communications: Board meeting notes, CEO directives, or high-level internal memos.
9. Software source code / IP assets: Proprietary code, scripts, or patent drafts.
10: Incident or security reports: Breaches, investigations, or sensitive operational incidents.

If any are found, please return their name in "flags" in the json, and a short explanation of why the page was flagged and the page and line number of the flag
Include all instances of any flag found, and include all flags found


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
{{

    "category": "<one of the four>", 
    "metadata": {{"pages": {given_page_num}, "images": {given_image_num}}},
    "flags" : <names of flags found>, 
    "citations": <list of flags in the format "page 2: SSN field">
}}
"""

    response = model.generate_content(prompt)
    return response.text 
