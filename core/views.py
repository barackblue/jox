from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from .models import *
from django.db.models import Q
from .forms import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from functools import wraps
from .models import OrganizationDoc
from .scraper import get_duckduckgo_urls, scrape_url_summary
from django.utils.text import Truncator
from urllib.parse import urlparse, urljoin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import logout

def admin_check(user):
    return user.is_superuser




def log_activity(user, action, article=None):
    if not user or not user.is_authenticated:
        return
    
    Activity.objects.create(
        user=user,
        action=action,
        article=article
    )


def about(request):
    return render(request, 'core/about.html')
def is_admin(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "You have no privileges to view this page.")
            return redirect('/')
    return _wrapped_view


@is_admin
def admin_dashboard(request):
    # dashboard logic
    return render(request, 'core/admin_dashboard.html')





def search_docs(request):
    query = request.GET.get('q', '').strip()  # Get the query string
    results = []

    if query:
        # Search in title or body (optional) using icontains
        results = Article.objects.filter(title__icontains=query, published=True)

    return render(request, 'core/search.html', {
        'query': query,
        'results': results
    })
class DocDetail(DetailView):
    model = OrganizationDoc
    template_name = 'core/doc_detail.html'

class ArticleList(ListView):
    model = Article
    template_name = 'core/articles.html'
    paginate_by = 10
    queryset = Article.objects.filter(published=True).order_by('-created_at')



class ArticleDetail(DetailView):
    model = Article
    template_name = 'core/article_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        log_activity(request.user, "view", obj)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['comment_form'] = CommentForm()
        return ctx


@method_decorator(login_required, name='dispatch')
class ArticleCreate(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'core/article_form.html'
    success_url = reverse_lazy('articles')

    # Automatically assign the logged-in user as the author
    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        log_activity(self.request.user, "publish", self.object)
        return response


def add_comment(request, slug):
    article = get_object_or_404(Article, slug=slug)
    form = CommentForm(request.POST or None)
    user = request.user if request.user.is_authenticated else None
    if form.is_valid():
        Comment.objects.create(user=user, article=article, body=form.cleaned_data['body'])
        log_activity(user, "comment", article)
    return redirect(article.get_absolute_url())

@login_required
def toggle_like(request, slug):
    article = get_object_or_404(Article, slug=slug)
    user = request.user
    like, created = Like.objects.get_or_create(user=user, article=article)
    if not created:
        like.delete()
        log_activity(user, "unlike", article)
    else:
        log_activity(user, "like", article)

        article.likes_count = article.likes.count()
        article.save(update_fields=['likes_count'])
        return JsonResponse({'liked': False, 'likes': article.likes_count})
    article.likes_count = article.likes.count()
    article.save(update_fields=['likes_count'])
    return JsonResponse({'liked': True, 'likes': article.likes_count})


class login(LoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'registration a success!!. Login now')
            return redirect('login')
        

        else:
            messages.error(request, 'something wen\'t wrong pleas try again')
    else:
        form = RegisterForm()
    
    return render(request, "core/register.html", {"form": form})

@login_required
def profile_edit(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        p_form = ProfileForm(request.POST, request.FILES, instance=profile)
        pw_form = PasswordChangeForm(user, request.POST)

        if 'update_profile' in request.POST and p_form.is_valid():
            p_form.save()
            messages.success(request, 'Profile updated successfully!')
            log_activity(user, "profile_update")
            return redirect('profile_edit')

        elif 'change_password' in request.POST and pw_form.is_valid():
            user = pw_form.save()
            update_session_auth_hash(request, user)  # keeps user logged in
            messages.success(request, 'Password updated successfully!')
            log_activity(user, "profile_update")
            return redirect('profile_edit')

        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        p_form = ProfileForm(instance=profile)
        pw_form = PasswordChangeForm(user)

    context = {
        'p_form': p_form,
        'pw_form': pw_form,
    }
    return render(request, 'core/profile_edit.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('articles')



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # Easy for now, later protect with JWT
def jumbo_chat(request):
    data = json.loads(request.body)
    user_message = data["message"]

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3", "prompt": user_message}
    )

    ai_text = response.json()["response"]
    return JsonResponse({"reply": ai_text})

@login_required
def my_articles(request):
    user_profile = request.user
    
    # Only get articles authored by this user
    articles = Article.objects.filter(author=user_profile).order_by('-created_at')
    
    return render(request, 'core/test.html', {
        'profile_user': user_profile,
        'articles': articles
    })


@login_required
def history(request):
    activities = request.user.activities.all()
    if request.method == "POST" and request.POST.get("clear_history"):
        activities.delete()
        messages.success(request, "All history cleared!")
        return redirect("history") 
    return render(request, "core/history.html", {"activities": activities})

@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, 'core/notifications.html', {'notifications': user_notifications})


@login_required
@user_passes_test(admin_check)
def send_notification(request):
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            notif = form.save(commit=False)
            notif.sender = request.user
            notif.save()
            return redirect('send_notification')  # reload page
    else:
        form = NotificationForm()
    return render(request, 'core/send_notification.html', {'form': form})
