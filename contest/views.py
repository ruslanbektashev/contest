from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views import View


class ProtectedUpload(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(status=200)
        response['Content-Type'] = ''
        response['X-Accel-Redirect'] = request.path
        return response
