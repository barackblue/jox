from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import LoginLog

@login_required
def login_history(request):
    logs = LoginLog.objects.filter(user=request.user).order_by("-timestamp")
    return render(request, "accounts/login_history.html", {"logs": logs})
