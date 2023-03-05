from django.urls import include, path
from contest_telegram_bot import views
from contest.settings import BOT_TOKEN

app_name = 'contest_telegram_bot'

urlpatterns = [
    path(f'{BOT_TOKEN}', views.bot_update, name='bot'),
]