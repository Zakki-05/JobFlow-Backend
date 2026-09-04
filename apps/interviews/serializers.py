from rest_framework import serializers
from .models import Interview, InterviewQuestion
from apps.applications.serializers import ApplicationSerializer

class InterviewSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='application.job.company', read_only=True)
    job_title = serializers.CharField(source='application.job.title', read_only=True)
    application_details = ApplicationSerializer(source='application', read_only=True)

    class Meta:
        model = Interview
        fields = [
            'id', 'user', 'application', 'application_details', 'company_name',
            'job_title', 'round', 'interview_date', 'interviewer', 'status',
            'notes', 'result', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']

class InterviewQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewQuestion
        fields = [
            'id', 'user', 'interview', 'company', 'role', 'round',
            'question', 'answer', 'difficulty', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']
