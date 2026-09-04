from django.urls import path
from .views import (
    InterviewListCreateView, InterviewDetailView,
    InterviewQuestionListCreateView, InterviewQuestionDetailView
)

urlpatterns = [
    path('', InterviewListCreateView.as_view(), name='interview_list_create'),
    path('<int:pk>/', InterviewDetailView.as_view(), name='interview_detail'),
    path('questions/', InterviewQuestionListCreateView.as_view(), name='question_list_create'),
    path('questions/<int:pk>/', InterviewQuestionDetailView.as_view(), name='question_detail'),
]
