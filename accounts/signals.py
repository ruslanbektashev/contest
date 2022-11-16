from accounts.models import Action


def log_user_login(sender, **kwargs):
    Action.objects.log_authorization(kwargs['user'], details=[{'action': "login"}])


def log_user_login_fail(sender, **kwargs):
    Action.objects.log_authorization(details=[{'action': "login_fail", 'credentials': kwargs['credentials']}])


def log_user_logout(sender, **kwargs):
    Action.objects.log_authorization(kwargs['user'], details=[{'action': "logout"}])
