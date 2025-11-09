from django.http import JsonResponse

def classify_view(request):
    """
    Placeholder view for document classification.
    Returns a simple JSON response for testing.
    """
    return JsonResponse({
        "message": "Classification endpoint is working!",
        "status": "ok"
    })
