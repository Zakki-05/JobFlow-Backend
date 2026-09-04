from django.db import models
from django.contrib.auth.models import User
from apps.jobs.models import Job
from apps.resumes.models import Resume

class Application(models.Model):
    STATUS_CHOICES = [
        ('SAVED', 'Saved'),
        ('APPLIED', 'Applied'),
        ('ASSESSMENT', 'Assessment'),
        ('INTERVIEW', 'Interview'),
        ('OFFER', 'Offer'),
        ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='application')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPLIED')
    applied_date = models.DateField(auto_now_add=True)
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True, related_name='applications_used')
    notes = models.TextField(blank=True)
    match_score = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_updated']

    def __str__(self):
        return f"{self.user.username} - {self.job.company} ({self.status})"

class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.application.job.company}: {self.status} on {self.created_at.strftime('%Y-%m-%d')}"

class FollowUp(models.Model):
    STATUS_CHOICES = [
        ('NEEDS_FOLLOWUP', 'Needs Follow-Up'),
        ('UPCOMING', 'Upcoming'),
        ('COMPLETED', 'Completed'),
    ]

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='followups')
    followup_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEEDS_FOLLOWUP')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['followup_date']

    def __str__(self):
        return f"Follow-up for {self.application.job.company} ({self.status})"
