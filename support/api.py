from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from support.models import TutorialStepPass

"""================================================ TutorialStepPass ================================================"""


class TutorialStepPassCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {'status': "OK"}
        view, step = request.data.get('view'), request.data.get('step')
        _, created = TutorialStepPass.objects.get_or_create(user=request.user, view=view, step=step)
        if not created:
            response['status'] = "Шаг руководства уже пройден"
        return JsonResponse(response)
