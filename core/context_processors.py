from .models import Article

def profile_sidebar(request):
    if request.user.is_authenticated:
        articles = Article.objects.filter(author=request.user)
        return {
            'profile_user': request.user,
            'profile_articles': articles,
        }
    return {}
