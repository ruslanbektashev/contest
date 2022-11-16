from django.apps import AppConfig
from django.contrib.auth import user_logged_in, user_logged_out, user_login_failed


class AccountsConfig(AppConfig):
    name = 'accounts'
    verbose_name = "Аккаунты"

    def ready(self):
        from accounts.signals import log_user_login, log_user_login_fail, log_user_logout
        user_logged_in.connect(log_user_login)
        user_logged_out.connect(log_user_logout)
        user_login_failed.connect(log_user_login_fail)
