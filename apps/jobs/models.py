from django.db import models
from django.contrib.auth.models import User
from apps.skills.models import Skill

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Internship', 'Internship'),
        ('Contract', 'Contract'),
    ]

    WORK_MODE_CHOICES = [
        ('Remote', 'Remote'),
        ('Hybrid', 'Hybrid'),
        ('On-site', 'On-site'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, default='Bengaluru')
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, default='Full-time')
    work_mode = models.CharField(max_length=50, choices=WORK_MODE_CHOICES, default='Remote')
    salary = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. ₹8 LPA - ₹15 LPA or ₹30,000/mo")
    job_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    required_skills_text = models.TextField(blank=True, help_text="Comma-separated skills string")
    preferred_skills_text = models.TextField(blank=True)
    experience_required = models.FloatField(default=1.0, help_text="Years of experience required")
    education = models.CharField(max_length=100, default="B.Tech / B.E.")
    source = models.CharField(max_length=100, default="Naukri.com")
    date_posted = models.DateField(blank=True, null=True)
    date_saved = models.DateTimeField(auto_now_add=True)
    is_applied = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_saved']

    def __str__(self):
        return f"{self.title} at {self.company}"

class JobSkill(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='job_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='job_instances')
    is_required = models.BooleanField(default=True)

    class Meta:
        unique_together = ('job', 'skill')

    def __str__(self):
        req = 'Required' if self.is_required else 'Preferred'
        return f"{self.job.title} - {self.skill.name} ({req})"
