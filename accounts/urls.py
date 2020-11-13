from django.conf import settings
from django.urls import path, include
from django.views.generic import TemplateView

from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('account/', include([
        path('create/set', views.AccountCreateSet.as_view(), name='account-create-set'),
        path('<int:pk>/', include([
            path('', views.AccountDetail.as_view(), name='account-detail'),
            path('update', views.AccountUpdate.as_view(), name='account-update'),
            path('subscribe/<str:object_model>/<int:object_id>/<int:open_discussion>', views.subscribe, name='account-subscribe'),
            path('unsubscribe/<str:object_model>/<int:object_id>/<int:open_discussion>', views.unsubscribe, name='account-unsubscribe'),
        ])),
        path('list', views.AccountFormList.as_view(), name='account-list'),
        path('credentials', views.AccountCredentials.as_view(), name='account-credentials'),
    ])),
    path('activity/', include([
        path('list', views.ActivityList.as_view(), name='activity-list'),
        path('mark', views.ActivityMark.as_view(), name='activity-mark'),
    ])),
    path('comment/', include([
        path('create', views.CommentCreate.as_view(), name='comment-create'),
        path('<int:pk>/', include([
            path('reply', views.CommentCreate.as_view(), name='comment-reply'),
            path('update', views.CommentUpdate.as_view(), name='comment-update'),
            path('delete', views.CommentDelete.as_view(), name='comment-delete'),
        ])),
    ])),
    path('message/<int:user_id>/create',
         views.MessageCreate.as_view() if settings.DEBUG else TemplateView.as_view(template_name='under_development.html'),
         name='message-create'),
    path('chat/list',
         views.ChatList.as_view() if settings.DEBUG else TemplateView.as_view(template_name='under_development.html'),
         name='chat-list'),
    path('announcement/', include([
        path('create', views.AnnouncementCreate.as_view(), name='announcement-create'),
        path('<int:pk>/', include([
            path('', views.AnnouncementDetail.as_view(), name='announcement-detail'),
            path('update', views.AnnouncementUpdate.as_view(), name='announcement-update'),
            path('delete', views.AnnouncementDelete.as_view(), name='announcement-delete')
        ])),
        path('list', views.AnnouncementList.as_view(), name='announcement-list'),
    ])),
    path('mark_comments_as_read', views.mark_comments_as_read, name='mark-comments-as-read'),
]
