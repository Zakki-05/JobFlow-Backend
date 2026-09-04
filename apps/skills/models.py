from django.db import models
from django.contrib.auth.models import User

class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('Frontend', 'Frontend'),
        ('Backend', 'Backend'),
        ('Database', 'Database'),
        ('DevOps', 'DevOps & Cloud'),
        ('Tools', 'Tools & Testing'),
        ('SoftSkills', 'Soft Skills'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category})"

class UserSkill(models.Model):
    PROFICIENCY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Expert', 'Expert'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='user_instances')
    proficiency = models.CharField(max_length=50, choices=PROFICIENCY_CHOICES, default='Intermediate')
    years_experience = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'skill')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.skill.name} ({self.proficiency})"
