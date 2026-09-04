from django.urls import path
from .views import MasterSkillListView, UserSkillListCreateView, UserSkillDetailView, SkillGapAnalysisView

urlpatterns = [
    path('master/', MasterSkillListView.as_view(), name='master_skills_list'),
    path('user/', UserSkillListCreateView.as_view(), name='user_skills_list'),
    path('user/<int:pk>/', UserSkillDetailView.as_view(), name='user_skill_detail'),
    path('gap-analysis/', SkillGapAnalysisView.as_view(), name='skill_gap_analysis'),
]
