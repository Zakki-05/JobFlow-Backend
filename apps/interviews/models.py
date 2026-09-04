from django.db import models
from django.contrib.auth.models import User
from apps.applications.models import Application

class Interview(models.Model):
    ROUND_CHOICES = [
        ('HR', 'HR Screen'),
        ('Technical', 'Technical Round'),
        ('Coding', 'Coding Assessment / Pair Coding'),
        ('Managerial', 'Managerial / Architecture'),
        ('Final', 'Final / On-site'),
    ]

    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    RESULT_CHOICES = [
        ('PENDING', 'Pending Result'),
        ('PASSED', 'Passed / Advanced'),
        ('FAILED', 'Failed / Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interviews')
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    round = models.CharField(max_length=50, choices=ROUND_CHOICES, default='Technical')
    interview_date = models.DateTimeField()
    interviewer = models.CharField(max_length=150, blank=True, help_text="Interviewer Name / Title")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    notes = models.TextField(blank=True)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['interview_date']

    def __str__(self):
        return f"{self.application.job.company} - {self.round} ({self.status})"

class InterviewQuestion(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recorded_questions')
    interview = models.ForeignKey(Interview, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    company = models.CharField(max_length=150)
    role = models.CharField(max_length=150, default='Software Engineer')
    round = models.CharField(max_length=50, default='Technical')
    question = models.TextField()
    answer = models.TextField(blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Medium')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company} - {self.question[:50]}"
