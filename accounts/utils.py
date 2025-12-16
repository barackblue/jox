#accounts
from django.contrib.gis.geoip2 import GeoIP2

def get_client_ip(request):
    x = request.META.get("HTTP_X_FORWARDED_FOR")
    return x.split(",")[0] if x else request.META.get("REMOTE_ADDR")

def get_location(ip):
    try:
        g = GeoIP2()
        city = g.city(ip).get("city", "")
        country = g.country(ip).get("country_name", "")
        return f"{city}, {country}"
    except:
        return "Unknown"
