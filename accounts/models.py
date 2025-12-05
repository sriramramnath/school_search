from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended user profile (for future use)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    verified = models.BooleanField(default=False)
    role = models.CharField(
        max_length=20, 
        choices=[('Parent', 'Parent'), ('Student', 'Student')],
        default='Parent'
    )
    language = models.CharField(max_length=50, default='English US')
    
    def __str__(self):
        return self.name or "Anonymous"
