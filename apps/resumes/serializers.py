from rest_framework import serializers
from .models import Resume

class ResumeSerializer(serializers.ModelSerializer):
    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = [
            'id', 'user', 'title', 'summary', 'education_data',
            'experience_data', 'projects_data', 'skills_summary',
            'certifications', 'file', 'file_name', 'is_default', 'applications_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'applications_count']

    def get_applications_count(self, obj):
        return obj.applications_used.count()
