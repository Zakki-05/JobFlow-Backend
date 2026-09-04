from django.urls import path
from .seed_views import SeedDataView

urlpatterns = [
    path('seed-data/', SeedDataView.as_view(), name='seed_data'),
]
