import mimetypes

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.utils.encoding import iri_to_uri
from django.views import View


class ProtectedUpload(LoginRequiredMixin, View):
    raise_exception = True

    def get(self, request, *args, **kwargs):
        content_type, encoding = mimetypes.guess_type(request.path)
        content_type = content_type or 'application/octet-stream'
        response = HttpResponse(content_type=content_type)
        if encoding:
            response['Content-Encoding'] = encoding
        try:
            response['X-Accel-Redirect'] = '/protected/' + iri_to_uri(request.path)
        except UnicodeEncodeError:
            raise Http404("Страница не найдена")
        return response
