from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    EDUCATION_LEVEL_CHOICES = [
        ('BTech', "B.Tech / B.E. (Computer Science / IT / Circuit)"),
        ('MTech', "M.Tech / M.E."),
        ('BCA_BSc', "BCA / B.Sc (Computer Science / IT)"),
        ('MCA_MSc', "MCA / M.Sc (Computer Science / IT)"),
        ('Doctorate', 'PhD / Doctorate'),
        ('SelfTaught', 'Self Taught / BootCamp'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    headline = models.CharField(max_length=255, blank=True, default='Software Development Engineer (SDE)')
    target_role = models.CharField(max_length=150, blank=True, default='Full Stack Developer / SDE')
    experience_years = models.FloatField(default=1.0)
    education_level = models.CharField(max_length=50, choices=EDUCATION_LEVEL_CHOICES, default='BTech')
    location = models.CharField(max_length=150, blank=True, default='Bengaluru / Remote')
    target_salary = models.IntegerField(default=1200000, help_text='Target annual salary in INR (₹) e.g. 1200000 for 12 LPA')
    github_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
