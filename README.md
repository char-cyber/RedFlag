connecting to venv: <your venv name>\Scripts\activate

running server: 
python manage.py runserver

making migrations for the app:
python manage.py migrate RedFlagApp


dependencies
pypdf
django 5.2.8
pymupdf

torch	Required backend for Hugging Face NER models
transformers	Hugging Face library for NLP models
pdfplumber	Extract text from PDFs
pymupdf (fitz)	Extract text, page info, bounding boxes
python-docx	Extract text from Word documents
pytesseract	OCR for scanned images / PDFs
regex	Advanced regex for PII patterns