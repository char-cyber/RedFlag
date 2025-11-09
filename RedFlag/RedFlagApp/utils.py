from pypdf import PdfReader
from django.http import HttpResponse

def preprocess(file_obj):
    result = {
        "is_pdf" : False,
        "num_pages": 0,
        "errors": []
    }
    #is pdf?
    try: 
        reader = PdfReader(file_obj)
        #count pages
        result["num_pages"] = len(reader.pages)

        result["is_pdf"] = True
    except Exception as e:
        result["is_pdf"] = False
        result["errors"].append(f"Invalid PDF: {str(e)}")

    return result
