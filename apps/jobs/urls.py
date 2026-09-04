from django.urls import path
from .views import (
    JobListCreateView, JobDetailView, JobAnalyzerExtractView,
    JobMatchCalculateView, SuitableJobsListView, ImportSuitableJobView,
    AIJobMatchView, AIJobRecommendationsView, AICareerAssistantView
)

urlpatterns = [
    path('', JobListCreateView.as_view(), name='job_list_create'),
    path('<int:pk>/', JobDetailView.as_view(), name='job_detail'),
    path('extract-skills/', JobAnalyzerExtractView.as_view(), name='job_extract_skills'),
    path('match-score/', JobMatchCalculateView.as_view(), name='job_match_score'),
    path('suitable-jobs/', SuitableJobsListView.as_view(), name='suitable_jobs_list'),
    path('import-job/', ImportSuitableJobView.as_view(), name='import_suitable_job'),
    path('ai-match/', AIJobMatchView.as_view(), name='job_ai_match'),
    path('ai-recommendations/', AIJobRecommendationsView.as_view(), name='job_ai_recommendations'),
    path('ai-assistant/', AICareerAssistantView.as_view(), name='job_ai_assistant'),
]
