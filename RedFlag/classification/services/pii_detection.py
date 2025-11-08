from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import pdfplumber

# Load the PII detection model
model_name = "SoelMgd/bert-pii-detection"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

#create pipeline
pii_pipeline = pipeline(
    "ner", 
    model=model, 
    tokenizer=tokenizer, 
    aggregation_strategy="simple"
)


def detect_pii_page(text, page_number):
    """
    Detect PII on a full page and map to line numbers.
    Returns a list of dictionaries.
    """
    detected_entities = pii_pipeline(text)
    
    # Split page into lines and track offsets
    lines = text.split("\n")
    line_offsets = []
    offset = 0
    for line in lines:
        line_offsets.append((offset, offset + len(line)))
        offset += len(line) + 1  # +1 for \n

    # Map entities to lines
    results = []
    for entity in detected_entities:
        if entity['score'] < 0.7:
            continue  # Skip low-confidence
        entity_start = entity['start']
        entity_end = entity['end']
        
        # Find which line it belongs to
        line_number = None
        for i, (start, end) in enumerate(line_offsets, start=1):
            if start <= entity_start < end:
                line_number = i
                break
        
        results.append({
            "type": entity['entity_group'].upper(),
            "score": entity['score'],
            "text": entity['word'],
            "start": entity_start,
            "end": entity_end,
            "page": page_number,
            "line": line_number
        })
    return results


def detect_pii_pdf(pdf_path):
    all_pii = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                page_pii = detect_pii_page(text, page_number)
                all_pii.extend(page_pii)
    return all_pii