from django.urls import path
from .views import (
    ApplicationListCreateView, ApplicationDetailView, ApplicationStatusUpdateView,
    FollowUpListCreateView, FollowUpDetailView
)

urlpatterns = [
    path('', ApplicationListCreateView.as_view(), name='application_list_create'),
    path('<int:pk>/', ApplicationDetailView.as_view(), name='application_detail'),
    path('<int:pk>/status/', ApplicationStatusUpdateView.as_view(), name='application_status_update'),
    path('followups/', FollowUpListCreateView.as_view(), name='followup_list_create'),
    path('followups/<int:pk>/', FollowUpDetailView.as_view(), name='followup_detail'),
]
