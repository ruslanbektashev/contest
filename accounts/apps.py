from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'
    verbose_name = "Аккаунты"

    def ready(self):
        from accounts.signals import receive_report_signal
