from django.core.exceptions import ImproperlyConfigured
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import ValidationError
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView

from accounts.models import Notification
from contests.forms import SubmissionFilesForm, SubmissionVerbalForm
from contests.models import Assignment, Problem, Submission
from contests.results import TaskProgress
from contests.tasks import evaluate_submission
from contests.templatetags.contests import colorize


class DjangoPermission(BasePermission):
    def get_permission_required(self, view):
        if view.permission_required is None:
            raise ImproperlyConfigured(
                '{0} is missing the permission_required attribute. Define {0}.permission_required, or override '
                '{1}.get_permission_required().'.format(view.__class__.__name__, self.__class__.__name__)
            )
        if isinstance(view.permission_required, str):
            perms = (view.permission_required,)
        else:
            perms = view.permission_required
        return perms

    def has_permission(self, request, view):
        perms = self.get_permission_required(view)
        return request.user.has_perms(perms)


class IsObjectOwner(BasePermission):
    def has_permission(self, request, view):
        return view.has_ownership()


class IsCourseLeader(BasePermission):
    def has_permission(self, request, view):
        return view.has_leadership()


@method_decorator(csrf_exempt, name='dispatch')
class SubmissionCreateAPI(APIView):
    permission_required = 'contests.add_submission'
    permission_classes = [IsAuthenticated, DjangoPermission]

    def post(self, request, *args, **kwargs):
        try:
            problem = Problem.objects.get(id=kwargs.pop('problem_id'))
        except Problem.DoesNotExist:
            return JsonResponse({'status': "Задача не найдена"}, status=404)
        try:
            assignment = Assignment.objects.get(user=self.request.user, problem=problem)
        except Assignment.DoesNotExist:
            assignment = None
        if problem.type == 'Verbal':
            form_class = SubmissionVerbalForm
        elif problem.type == 'Files':
            form_class = SubmissionFilesForm
        else:
            return JsonResponse({'status': "Создать посылку через телеграм-бота можно только для задач типа Устный "
                                           "ответ и Файлы"}, status=400)
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.instance.owner = request.user
            form.instance.problem = problem
            form.instance.assignment = assignment
            form.save()
            return JsonResponse({'status': "OK"})
        else:
            return JsonResponse({'status': "Ошибка валидации", 'errors': form.errors.get_json_data()})


class SubmissionEvaluateAPI(APIView):
    permission_required = 'contests.evaluate_submission'
    permission_classes = [IsAuthenticated, DjangoPermission | IsObjectOwner | IsCourseLeader]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['sandbox_type'] = request.GET.get('sandbox', 'subprocess')
        return super().dispatch(request, *args, **kwargs)

    def has_ownership(self):
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        return self.object.owner_id == self.request.user.id

    def has_leadership(self):
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        return self.object.course.leaders.filter(id=self.request.user.id).exists()

    def get_object(self):
        return Submission.objects.get(pk=self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        if self.object.problem.type == 'Program' and self.object.problem.is_testable:
            task = evaluate_submission.delay(self.object.pk, request.user.id, **self.storage)
            self.object.task_id = task.id
            self.object.save()
            return JsonResponse({'status': "OK", 'task_id': task.id})
        return JsonResponse({'status': "Делать нечего"})


class SubmissionProgressAPI(APIView):
    permission_required = 'contests.evaluate_submission'
    permission_classes = [IsAuthenticated, DjangoPermission | IsObjectOwner | IsCourseLeader]

    def has_ownership(self):
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        return self.object.owner_id == self.request.user.id

    def has_leadership(self):
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        return self.object.course.leaders.filter(id=self.request.user.id).exists()

    def get_object(self):
        return Submission.objects.get(pk=self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):
        task_id = self.kwargs.get('task_id')
        progress = TaskProgress(task_id)
        return JsonResponse(progress.get_info())


class SubmissionUpdateSerializer(ModelSerializer):
    ALLOWED_STATUSES = ('OK', 'PS', 'TF', 'WA', 'NA', 'EV', 'UN')

    class Meta:
        model = Submission
        fields = ['status', 'score']

    def validate_status(self, value):
        if value not in self.ALLOWED_STATUSES:
            raise ValidationError("Статус недопустим для данного типа посылки", code='status_not_allowed')
        return value

    def validate_score(self, value):
        if value > self.instance.problem.score_max:
            raise ValidationError("Оценка не может превышать максимальную оценку этой задачи",
                                  code='score_exceeds_problem_score_max')
        return value

    def validate(self, attrs):
        if self.instance.problem.type == 'Program' and self.instance.problem.is_testable:
            raise ValidationError("Посылки к этой задаче проверяются автоматически", code='problem_is_testable')
        return attrs


class SubmissionUpdateAPI(UpdateAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionUpdateSerializer
    permission_required = 'contests.change_submission'
    permission_classes = [IsAuthenticated, DjangoPermission | IsObjectOwner | IsCourseLeader]

    def has_ownership(self):
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        return self.object.course.owner_id == self.request.user.id

    def has_leadership(self):
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        return self.object.course.leaders.filter(id=self.request.user.id).exists()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.object if hasattr(self, 'object') else self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        response = {
            'status': "OK",
            'updated': [
                {
                    'id': instance.id,
                    'status': instance.status,
                    'status_display': instance.get_status_display(),
                    'score': instance.score,
                    'score_percentage': instance.get_score_percentage(),
                    'color': colorize(instance.status)
                }
            ]
        }
        if instance.main_submission is not None:
            response['updated'].append({
                'id': instance.main_submission.id,
                'status': instance.main_submission.status,
                'status_display': instance.main_submission.get_status_display(),
                'score': instance.main_submission.score,
                'score_percentage': instance.main_submission.get_score_percentage(),
                'color': colorize(instance.main_submission.status)
            })
            Notification.objects.notify(instance.owner, subject=request.user, action="изменил оценку Вашей посылки",
                                        object=instance, relation="из раздела", reference=instance.contest)
        return JsonResponse(response)

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
