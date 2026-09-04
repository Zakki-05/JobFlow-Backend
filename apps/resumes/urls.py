from django.urls import path
from .views import ResumeListCreateView, ResumeDetailView, ParseResumeFileView, AIResumeAnalyzeView

urlpatterns = [
    path('', ResumeListCreateView.as_view(), name='resume_list_create'),
    path('<int:pk>/', ResumeDetailView.as_view(), name='resume_detail'),
    path('parse-file/', ParseResumeFileView.as_view(), name='resume_parse_file'),
    path('ai-analyze/', AIResumeAnalyzeView.as_view(), name='resume_ai_analyze'),
]
