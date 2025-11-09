from io import BytesIO
from pypdf import PdfReader
import fitz  # PyMuPDF
from docx import Document

def preprocess(file_obj):
    """
    Analyze file (PDF or DOCX):
    - Check validity
    - Count pages or sections
    - Count images
    - Extract basic metadata
    """

    result = {
        "is_pdf": False,
        "is_docx": False,
        "num_pages": 0,
        "num_images": 0,
        "errors": [],
        "file_type": None
    }

    filename = getattr(file_obj, "name", "").lower()

    try:
        # Read file into memory once (works for Django InMemoryUploadedFile)
        file_data = file_obj.read()
        buffer = BytesIO(file_data)

        # --- PDF Handling ---
        if filename.endswith(".pdf"):
            result["file_type"] = "PDF"
            try:
                reader = PdfReader(buffer)
                result["num_pages"] = len(reader.pages)
                buffer.seek(0)
                result["num_images"] = count_images(buffer)
                result["is_pdf"] = True
            except Exception as e:
                result["errors"].append(f"Invalid PDF: {str(e)}")

        # --- DOCX Handling ---
        elif filename.endswith(".docx"):
            result["file_type"] = "DOCX"
            try:
                buffer.seek(0)
                doc = Document(buffer)
                # Approximate "pages" = 1 for every 800 words
                text = "\n".join([p.text for p in doc.paragraphs])
                word_count = len(text.split())
                result["num_pages"] = max(1, word_count // 800)
                # Count images
                result["num_images"] = len(doc.inline_shapes)
                result["is_docx"] = True
            except Exception as e:
                result["errors"].append(f"Invalid DOCX: {str(e)}")

        # --- Unsupported ---
        else:
            result["errors"].append("Unsupported file type")

    except Exception as e:
        result["errors"].append(f"File processing error: {str(e)}")

    return result


def count_images(buffer):
    """Count images inside a PDF (PyMuPDF)."""
    total_images = 0
    try:
        pdf_doc = fitz.open(stream=buffer.read(), filetype="pdf")
        for page in pdf_doc:
            # Works for all PyMuPDF versions
            if hasattr(page, "get_images"):
                images = page.get_images()
            else:
                images = page.getImageList()
            total_images += len(images)
    except Exception as e:
        print(f"[WARN] Failed to count images: {e}")
    return total_images