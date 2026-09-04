from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Count
from apps.jobs.models import Job
from apps.applications.models import Application, FollowUp
from apps.interviews.models import Interview, InterviewQuestion
from apps.skills.models import UserSkill, Skill

class AnalyticsOverviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        # Core counters
        total_saved_jobs = Job.objects.filter(user=user).count()
        total_applications = Application.objects.filter(user=user).count()
        apps_this_month = Application.objects.filter(user=user, applied_date__gte=thirty_days_ago.date()).count()
        
        interviews_count = Application.objects.filter(user=user, status='INTERVIEW').count()
        offers_count = Application.objects.filter(user=user, status='OFFER').count()
        rejections_count = Application.objects.filter(user=user, status='REJECTED').count()
        assessments_count = Application.objects.filter(user=user, status='ASSESSMENT').count()

        # Responses count = any status beyond APPLIED (Assessment, Interview, Offer, Rejected)
        responded_count = Application.objects.filter(
            user=user,
            status__in=['ASSESSMENT', 'INTERVIEW', 'OFFER', 'REJECTED']
        ).count()

        response_rate = round((responded_count / total_applications * 100), 1) if total_applications > 0 else 0.0
        offer_rate = round((offers_count / total_applications * 100), 1) if total_applications > 0 else 0.0
        interview_rate = round((interviews_count / total_applications * 100), 1) if total_applications > 0 else 0.0

        # Application Funnel Data
        funnel = [
            {'stage': 'Applications', 'count': total_applications},
            {'stage': 'Responses', 'count': responded_count},
            {'stage': 'Assessments', 'count': assessments_count},
            {'stage': 'Interviews', 'count': interviews_count},
            {'stage': 'Offers', 'count': offers_count},
        ]

        # Top target roles & companies
        top_companies = list(
            Job.objects.filter(user=user)
            .values('company')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        top_roles = list(
            Job.objects.filter(user=user)
            .values('title')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        # Upcoming interviews & follow-up alerts count
        upcoming_interviews = Interview.objects.filter(
            user=user,
            interview_date__gte=now,
            status='SCHEDULED'
        ).count()

        needs_followup_count = FollowUp.objects.filter(
            application__user=user,
            status='NEEDS_FOLLOWUP'
        ).count()

        return Response({
            'kpis': {
                'total_saved_jobs': total_saved_jobs,
                'total_applications': total_applications,
                'apps_this_month': apps_this_month,
                'interviews_count': interviews_count,
                'offers_count': offers_count,
                'rejections_count': rejections_count,
                'response_rate': response_rate,
                'interview_rate': interview_rate,
                'offer_rate': offer_rate,
                'upcoming_interviews_count': upcoming_interviews,
                'needs_followup_count': needs_followup_count
            },
            'funnel': funnel,
            'top_companies': top_companies,
            'top_roles': top_roles
        })
