# import re

# from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# model_name = "iiiorg/piiranha-v1-detect-personal-information"
# #other option dbmdz/bert-large-cased-finetuned-conll03-english
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForTokenClassification.from_pretrained(model_name)

# ner_pipeline = pipeline(
#     "ner", 
#     model=model, 
#     tokenizer=tokenizer, 
#     aggregation_strategy="simple"
# )


def detect_pii(text):
    # flags = []

    # if isinstance(text, tuple):
    #     text_content = text[0]  # take full text
    # elif isinstance(text, dict):
    #     text_content = "\n".join(str(t) for t in text.values())
    # elif isinstance(text, list):
    #     text_content = "\n".join(str(t) for t in text)
    # else:
    #     text_content = str(text)


    # entities = ner_pipeline(text_content, truncation=True)
    # for e in entities:
    #     flags.append({
    #         "type": "NER",
    #         "entity_group": e["entity_group"],
    #         "text": e["word"],
    #         "score": e["score"]
    #     })

    return "hi"
