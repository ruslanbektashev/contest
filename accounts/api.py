from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from accounts.models import Comment, Notification

"""==================================================== Comment ====================================================="""


class CommentMarkAsReadAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if hasattr(request.data, 'getlist'):
            unread_comments_ids = request.data.getlist('unread_comments_ids', None)
        else:
            unread_comments_ids = request.data.get('unread_comments_ids', None)
        if not unread_comments_ids:
            return JsonResponse({'status': "Нечего помечать"})
        if unread_comments_ids:
            account = request.user.account
            unread_comments = Comment.objects.filter(id__in=unread_comments_ids).exclude(author=request.user)
            unread_comments = unread_comments.exclude(id__in=account.comments_read.values_list('id', flat=True))
            account.mark_comments_as_read(unread_comments)
        return JsonResponse({'status': "OK"})


"""================================================== Notification =================================================="""


class NotificationMarkAsReadAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if hasattr(request.data, 'getlist'):
            unread_notifications_ids = request.data.getlist('unread_notifications_ids', None)
        else:
            unread_notifications_ids = request.data.get('unread_notifications_ids', None)
        if not unread_notifications_ids:
            return JsonResponse({'status': "Нечего помечать"})
        unread_notifications = Notification.objects.filter(id__in=unread_notifications_ids, recipient=request.user)
        unread_notifications.mark_as_read()
        return JsonResponse({'status': "OK"})
