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

def extract_text_with_positions(uploaded_file):
    """
    Extracts text, page number, line number, and position from a PDF.
    Returns a list of dicts:
    [
        {
            'page': 1,
            'line': 1,
            'text': 'John Doe',
            'bbox': (x0, y0, x1, y1)
        },
        ...
    ]
    """
    results = []

    # Make sure the file pointer is at the start
    uploaded_file.seek(0)
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("blocks")  # each block = (x0, y0, x1, y1, text, ...)
        line_counter = 0  # track line numbers per page

        for b in blocks:
            block_text = b[4].strip()
            if block_text:
                lines = block_text.split('\n')  # split block into lines
                for line in lines:
                    line = line.strip()
                    if line:  # skip empty lines
                        line_counter += 1
                        results.append({
                            "page": page_num,
                            "line": line_counter,
                            "text": line,
                            "bbox": (b[0], b[1], b[2], b[3])
                        })

    return results
