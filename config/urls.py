from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/jobs/', include('apps.jobs.urls')),
    path('api/applications/', include('apps.applications.urls')),
    path('api/skills/', include('apps.skills.urls')),
    path('api/resumes/', include('apps.resumes.urls')),
    path('api/interviews/', include('apps.interviews.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/seed/', include('apps.analytics.seed_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
