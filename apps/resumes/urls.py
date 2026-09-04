from django.urls import path
from .views import ResumeListCreateView, ResumeDetailView, ParseResumeFileView

urlpatterns = [
    path('', ResumeListCreateView.as_view(), name='resume_list_create'),
    path('<int:pk>/', ResumeDetailView.as_view(), name='resume_detail'),
    path('parse-file/', ParseResumeFileView.as_view(), name='resume_parse_file'),
]
