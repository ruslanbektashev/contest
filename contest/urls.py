"""contest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path('login', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout', auth_views.logout_then_login, name='logout'),
    path('password/', include([
        path('change/', include([
            path('', auth_views.PasswordChangeView.as_view(), name='password-change'),
            path('done', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done')
        ])),
        path('reset/', include([
            path('', auth_views.PasswordResetView.as_view(), name='password-reset'),
            path('done', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
            path('<uidb64>/<token>/confirm', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
            path('complete', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete')
        ]))
    ])),
    path('accounts/', include('accounts.urls')),
    path('', include('contests.urls')),
    path('schedule/', include('schedule.urls')),
    path('support/', include('support.urls')),
    path('contest-telegram-bot/', include('contest_telegram_bot.urls')),
    path('admin/', admin.site.urls),
] + (static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +
     static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
