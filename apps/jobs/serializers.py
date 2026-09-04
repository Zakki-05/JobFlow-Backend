from rest_framework import serializers
from .models import Job, JobSkill
from apps.skills.serializers import SkillSerializer

class JobSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)

    class Meta:
        model = JobSkill
        fields = ['id', 'skill', 'is_required']

class JobSerializer(serializers.ModelSerializer):
    job_skills = JobSkillSerializer(many=True, read_only=True)
    application_status = serializers.SerializerMethodField()
    application_id = serializers.SerializerMethodField()
    match_score = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id', 'user', 'title', 'company', 'location', 'job_type', 'work_mode',
            'salary', 'job_url', 'description', 'required_skills_text',
            'preferred_skills_text', 'experience_required', 'education', 'source',
            'date_posted', 'date_saved', 'is_applied', 'notes',
            'job_skills', 'application_status', 'application_id', 'match_score'
        ]
        read_only_fields = ['user', 'date_saved']

    def get_application_status(self, obj):
        if hasattr(obj, 'application'):
            return obj.application.status
        return 'SAVED' if not obj.is_applied else 'APPLIED'

    def get_application_id(self, obj):
        if hasattr(obj, 'application'):
            return obj.application.id
        return None

    def get_match_score(self, obj):
        if hasattr(obj, 'application'):
            return obj.application.match_score
        return 0.0
