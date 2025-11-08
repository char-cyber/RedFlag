from pypdf import PdfReader
from django.http import HttpResponse
import fitz
from io import BytesIO


def preprocess(file_obj):
    result = {
        "is_pdf" : False,
        "num_pages": 0,
        "errors": []
    }
    #is pdf?
    try: 
        # Read the file into memory buffer (works for Django InMemoryUploadedFile)
        file_data = file_obj.read()
        buffer = BytesIO(file_data)

        # Validate + count pages
        reader = PdfReader(buffer)

        #count pages
        result["num_pages"] = len(reader.pages)

        buffer.seek(0)
        result["num_images"] = count_images(buffer) 
        result["is_pdf"] = True

    except Exception as e:
        result["is_pdf"] = False
        result["errors"].append(f"Invalid PDF: {str(e)}")

    return result


def count_images(buffer):
    """Count images in PDF from memory buffer."""
    total_images = 0
    try:
        pdf_doc = fitz.open(stream=buffer.read(), filetype="pdf")
        for page in pdf_doc:
            total_images += len(page.get_images())
    except Exception as e:
        print(f"[WARN] count_images failed: {e}")
    return total_images

import fitz  # PyMuPDF

def extract_text_from_file(uploaded_file):
    """
    Extract text from a PDF file uploaded via Django.
    Returns either a single string or a dict with pages.
    """
    document_text = ""
    pages_text = {}
    
    # Open PDF in memory
    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    
    for page_number in range(len(pdf)):
        page = pdf[page_number]
        text = page.get_text()
        pages_text[page_number + 1] = text
        document_text += text + "\n"
    
    return document_text, pages_text
