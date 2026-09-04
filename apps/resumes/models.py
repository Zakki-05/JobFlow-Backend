from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=200, default='Default Software Engineering Resume')
    summary = models.TextField(blank=True, default='Passionate software engineer with strong full-stack skills.')
    education_data = models.TextField(blank=True, default='B.S. in Computer Science')
    experience_data = models.TextField(blank=True, default='Software Engineer Intern | Developed REST APIs & React UI')
    projects_data = models.TextField(blank=True, default='JobFlow SaaS Platform, E-Commerce App')
    skills_summary = models.TextField(blank=True, default='React, JavaScript, Python, Django, MySQL, Git, Tailwind CSS')
    certifications = models.TextField(blank=True)
    file = models.FileField(upload_to='resumes/', null=True, blank=True)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    is_default = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"
