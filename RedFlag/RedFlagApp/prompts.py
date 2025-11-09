prompt_library = {
    "root": [
        "How many pages in the document",
        "How many images in the document",
        "Confirm presence or absence of PII",
        "Mention if content is safe for kids",
        "Given the following document context and prompt, respond ONLY with JSON including these keys: {confidence} : <number between 0 and 1 (how sure you are about your answer>",
],
    "Sensitive/ Highly Sensitive": [
        "Cite pages containing SSNs if any",
        "Cite pages containing account/credit card numbers if any",
        "Cite pages containing propreity schematics such as defense or next-gen product designs or military equipment if any",
        "Explain how the sensitive information in this document should be handled.",
        "Show redaction recommendations for this document.",
    ],
    'Confidential': [
        "Identify any confidential information in this document",
        "Cite internal communications if any"
        "Cite non-public operational content details if there are any",
        "Cite business documents if any",
        "Cite customer details such as names and addresses if any"
        "Cite the region with the serial if any",
        "Explain policy mapping for indentifiable equipment if any",
        "List potential risks if this document is shared without proper authorization.",
    ],
    'Public': [
        "Explain why this document is classified as public.",
        "Cite pages containing public marketing statements if any",
        "Cite pages containing public product brochures if any",
        "Cite pages containing public website content if any",
        "Cite pages containing public generic images if any",
        "Confirm absence of PII and confidential information",
        "Summarize the document and set its classification as safe.",
    ],
    'Unsafe': [
        "List out which policies were violated amongst hate speech, exploitative content, violent content, political news, or cyber-threat content",
        "Cite pages containing hate speech if any",
        "Cite pages containing exploitative content if any",
        "Cite pages containing violent content if any",
        "Cite pages containing political news if any",
        "Cite pages containing cyber-threat content if any",
    ]
}