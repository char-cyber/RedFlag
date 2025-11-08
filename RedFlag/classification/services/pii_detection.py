from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline


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


def detect_pii(text, page=None, line=None):
    """
    Detect PII in the text using pii_pipeline.
    """
    pii = []
    pii_flags = pii_pipeline(text)
    
    for flag in pii_flags:
        if flag['score'] > 0.7:
            entity_info = {
                "type": flag['entity_group'].upper(),
                "score": flag['score'],
                "text": flag['word'],
                "start": flag['start'],
                "end": flag['end'],
                "page": page,
                "line": line
            }
            pii.append(entity_info)
    
    return pii