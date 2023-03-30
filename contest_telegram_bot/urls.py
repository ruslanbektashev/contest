from django.conf import settings
from django.urls import path

from contest_telegram_bot import views

app_name = 'contest_telegram_bot'

urlpatterns = [
    path(f'{settings.BOT_TOKEN}', views.bot_update, name='bot'),
]
