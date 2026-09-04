from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from .models import Skill, UserSkill
from .serializers import SkillSerializer, UserSkillSerializer
from apps.jobs.models import Job, JobSkill

class MasterSkillListView(generics.ListCreateAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserSkillListCreateView(generics.ListCreateAPIView):
    serializer_class = UserSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSkill.objects.filter(user=self.request.user)

class UserSkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSkill.objects.filter(user=self.request.user)

class SkillGapAnalysisView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        user_skills = set(
            UserSkill.objects.filter(user=user).values_list('skill__name', flat=True)
        )
        user_skills_lower = {s.lower() for s in user_skills}

        saved_jobs = Job.objects.filter(user=user)
        total_jobs_count = saved_jobs.count()

        # Collect required skills from Job text and JobSkill instances
        skill_counts = {}
        for job in saved_jobs:
            job_req_skills = set()
            if job.required_skills_text:
                for sk in job.required_skills_text.split(','):
                    sk_clean = sk.strip()
                    if sk_clean:
                        job_req_skills.add(sk_clean)
            
            # Also check linked JobSkill models
            linked_skills = JobSkill.objects.filter(job=job).values_list('skill__name', flat=True)
            for sk in linked_skills:
                job_req_skills.add(sk)

            for sk in job_req_skills:
                sk_title = sk.title()
                skill_counts[sk_title] = skill_counts.get(sk_title, 0) + 1

        strong_skills = []
        missing_skills = []

        for skill_name, frequency in skill_counts.items():
            item = {
                'skill_name': skill_name,
                'job_count': frequency,
                'demand_percentage': round((frequency / total_jobs_count * 100), 1) if total_jobs_count > 0 else 0
            }
            if skill_name.lower() in user_skills_lower:
                strong_skills.append(item)
            else:
                missing_skills.append(item)

        # Sort missing skills by frequency descending to present Priority Skills roadmap
        missing_skills.sort(key=lambda x: x['job_count'], reverse=True)
        strong_skills.sort(key=lambda x: x['job_count'], reverse=True)

        return Response({
            'total_saved_jobs': total_jobs_count,
            'user_skills_count': len(user_skills),
            'strong_skills': strong_skills,
            'missing_skills': missing_skills,
            'priority_roadmap': missing_skills[:10]  # Top 10 priority skill gaps
        })
