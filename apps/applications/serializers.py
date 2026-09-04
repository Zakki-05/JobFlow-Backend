from rest_framework import serializers
from .models import Application, ApplicationStatusHistory, FollowUp
from apps.jobs.serializers import JobSerializer
from apps.resumes.serializers import ResumeSerializer

class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStatusHistory
        fields = ['id', 'status', 'notes', 'created_at']

class FollowUpSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='application.job.company', read_only=True)
    job_title = serializers.CharField(source='application.job.title', read_only=True)

    class Meta:
        model = FollowUp
        fields = [
            'id', 'application', 'company_name', 'job_title',
            'followup_date', 'status', 'notes', 'created_at'
        ]

class ApplicationSerializer(serializers.ModelSerializer):
    job_details = JobSerializer(source='job', read_only=True)
    job_id = serializers.IntegerField(write_only=True, required=False)
    resume_details = ResumeSerializer(source='resume', read_only=True)
    status_history = ApplicationStatusHistorySerializer(many=True, read_only=True)
    followups = FollowUpSerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'user', 'job', 'job_id', 'job_details', 'status',
            'applied_date', 'resume', 'resume_details', 'notes',
            'match_score', 'last_updated', 'status_history', 'followups'
        ]
        read_only_fields = ['user', 'applied_date', 'last_updated', 'job']
