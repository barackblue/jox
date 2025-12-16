from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import LoginLog
from .utils import get_client_ip, get_location
from django.core.mail import send_mail

@receiver(user_logged_in)
def create_login_log(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")
    location = get_location(ip)

    previous_logs = LoginLog.objects.filter(user=user)

    is_first = previous_logs.count() == 0
    is_new_device = not previous_logs.filter(user_agent=user_agent).exists()

    LoginLog.objects.create(
        user=user,
        ip_address=ip,
        location=location,
        user_agent=user_agent,
        is_first_login=is_first,
        is_new_device=is_new_device,
    )

    # Email alerts
    if is_first:
        send_mail(
            subject="Welcome! First Login",
            message=f"Hi {user.username}, this is your first login.",
            from_email=None,
            recipient_list=[user.email],
            fail_silently=True,
        )

    elif is_new_device:
        send_mail(
            subject="New Device Login",
            message=(
                f"Hi {user.username},\n\n"
                f"A new device just logged into your account.\n"
                f"IP: {ip}\nLocation: {location}"
            ),
            from_email=None,
            recipient_list=[user.email],
            fail_silently=True,
        )
