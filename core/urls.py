from django.urls import path
from . import views
from .views import login
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.ArticleList.as_view(), name='articles'),
    path('search/', views.search_docs, name='search'),
    path('article/new/', views.ArticleCreate.as_view(), name='article_new'),
    path('article/<slug:slug>/', views.ArticleDetail.as_view(), name='article_detail'),
    path('article/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('article/<slug:slug>/like/', views.toggle_like, name='toggle_like'),
    path('login/', login.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('profile_edit', views.profile_edit, name='profile_edit'),
    path('logout/', views.logout_view, name='logout'),
    path("jumbo/chat/", views.jumbo_chat, name="jumbo_chat"),
    path('test/', views.my_articles, name='test'),
    path('about/', views.about, name='about'),
    path('history/', views.history, name='history'),
    path('notifications/', views.notifications, name='notifications'),
    path('send_notification/', views.send_notification, name='send_notification'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
