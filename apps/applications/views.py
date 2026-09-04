from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Application, ApplicationStatusHistory, FollowUp
from .serializers import ApplicationSerializer, ApplicationStatusHistorySerializer, FollowUpSerializer
from apps.jobs.models import Job
from apps.jobs.matching_engine import calculate_job_match_score
from apps.skills.models import UserSkill

class ApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Application.objects.filter(user=self.request.user)
        status_param = self.request.query_params.get('status', None)
        if status_param and status_param != 'ALL':
            queryset = queryset.filter(status=status_param)
        return queryset.order_by('-last_updated')

    def perform_create(self, serializer):
        job_id = self.request.data.get('job_id')
        job = Job.objects.get(id=job_id, user=self.request.user)
        
        # Calculate JobMatch score upon application creation
        user_profile = getattr(self.request.user, 'profile', None)
        user_skills = UserSkill.objects.filter(user=self.request.user).select_related('skill')
        job_data = {
            'description': job.description,
            'required_skills_text': job.required_skills_text,
            'experience_required': job.experience_required,
            'education': job.education,
            'work_mode': job.work_mode,
            'location': job.location
        }
        match_result = calculate_job_match_score(job_data, user_profile, user_skills)
        score = match_result.get('overall_match_score', 75.0)

        app_status = self.request.data.get('status', 'APPLIED')
        application = serializer.save(
            user=self.request.user,
            job=job,
            match_score=score,
            status=app_status
        )

        # Mark job as applied
        job.is_applied = True
        job.save()

        # Log initial status history
        ApplicationStatusHistory.objects.create(
            application=application,
            status=app_status,
            notes='Application tracked.'
        )

class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)

class ApplicationStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            app_obj = Application.objects.get(pk=pk, user=request.user)
        except Application.DoesNotExist:
            return Response({'error': 'Application not found.'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        notes = request.data.get('notes', '')

        if not new_status:
            return Response({'error': 'New status required.'}, status=status.HTTP_400_BAD_REQUEST)

        app_obj.status = new_status
        if notes:
            app_obj.notes = notes
        app_obj.save()

        # Create history entry
        ApplicationStatusHistory.objects.create(
            application=app_obj,
            status=new_status,
            notes=notes or f"Status changed to {new_status}"
        )

        serializer = ApplicationSerializer(app_obj)
        return Response(serializer.data)

class FollowUpListCreateView(generics.ListCreateAPIView):
    serializer_class = FollowUpSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = FollowUp.objects.filter(application__user=self.request.user)
        status_param = self.request.query_params.get('status', None)
        if status_param and status_param != 'ALL':
            queryset = queryset.filter(status=status_param)
        return queryset

class FollowUpDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FollowUpSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FollowUp.objects.filter(application__user=self.request.user)
