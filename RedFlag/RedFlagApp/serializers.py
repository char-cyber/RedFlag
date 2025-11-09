from rest_framework import serializers

class ContextQuerySerializer(serializers.Serializer):
    query = serializers.CharField()
    document_id = serializers.IntegerField(required = False)
    #add more fields if necessary such as filename and file upload

class HITLFeedbackSerializer(serializers.Serializer):
    query = serializers.CharField(required = False)
    document_id = serializers.IntegerField()
    categories = serializers.ListField(child = serializers.CharField(), required =False)
    citations = serializers.ListField(child = serializers.CharField(), required = False)
    flags = serializers.ListField(child = serializers.CharField(), required = False)
    metadata = serializers.DictField(required = False)
    confidence= serializers.FloatField(required = False)
    edge_case = serializers.BooleanField(required = False)
    status = serializers.CharField(required = False)
    prompt_feedback = serializers.ListField(child = serializers.CharField(), required = False)
    comments = serializers.CharField(required = False, allow_blank=True)
    
    