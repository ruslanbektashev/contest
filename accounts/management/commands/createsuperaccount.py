from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Account, Faculty
from support.models import Discussion

class Command(BaseCommand):
    help = "Команда создаст супераккаунт в пару к суперпользователю."

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        if users.count() != 1:
            self.stderr.write(self.style.ERROR("Что-то не так, пользователей больше 1 :("))
            return
        superuser = users.get()
        accounts = Account.objects.all()
        if accounts.count() != 0:
            self.stderr.write(self.style.ERROR("Что-то не так, аккаунты уже существуют :("))
            return
        faculties = Faculty.objects.all()
        if faculties.count() != 0:
            self.stderr.write(self.style.ERROR("Что-то не так, факультеты уже существуют :("))
            return
        faculty = Faculty.objects.create(
            name="Прикладная Математика и Информатика",
            group_name="Математики",
            group_prefix="М",
            short_name="Математики"
        )
        Account.objects.create(user_id=superuser.id, faculty=faculty, level=1, admission_year=timezone.now().year, type=3)
        Discussion.objects.create(owner_id=superuser.id, topic="Чат с разработчиками")
