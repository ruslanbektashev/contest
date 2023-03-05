import telebot

from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from contest_telegram_bot.bot import tbot


@csrf_exempt
def bot_update(request):
    print(request.body)
    if request.method == 'POST':
        json_data = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_data)
        tbot.process_new_updates([update])
        return HttpResponse('ok', status=200)
    else:
        raise Http404



