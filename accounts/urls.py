from django.urls import path
from .views import login_history

urlpatterns = [
    path('login_history/', login_history, name='login_history'),
]
