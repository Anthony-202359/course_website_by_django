from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Subscription(models.Model):
    PLAN_CHOICES = [
        ("free", "Free"),
        ("intermediate", "Intermediate"),
        ("pro", "Pro"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="free")
    active = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan}"

class Course(models.Model):
    TIER_CHOICES = [
        ("free", "Free"),
        ("intermediate", "Intermediate"),
        ("pro", "Pro"),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default="free")
    content = models.TextField()
    image = models.ImageField(upload_to="course_images/", blank=True, null=True)

    def __str__(self):
        return self.title
