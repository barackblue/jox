from django.db import models
from django.contrib.auth.models import User

class LoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=100)
    user_agent = models.TextField()
    location = models.CharField(max_length=255, blank=True, null=True)
    is_new_device = models.BooleanField(default=False)
    is_first_login = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} logged in at {self.timestamp}"
