from django.urls import path, include

from accounts import views
from contest.utils import under_development

app_name = 'accounts'

urlpatterns = [
    path('account/', include([
        path('create/set', views.AccountCreateSet.as_view(), name='account-create-set'),
        path('update/set', views.AccountUpdateSet.as_view(), name='account-update-set'),
        path('<int:pk>/', include([
            path('', views.AccountDetail.as_view(), name='account-detail'),
            path('update', views.AccountUpdate.as_view(), name='account-update'),
            path('course/<int:course_id>/results', views.AccountCourseResults.as_view(), name='account-course-results'),
            path('problem/<int:problem_id>/submissions', views.AccountProblemSubmissionList.as_view(), name='account-problem-submissions'),
            path('assignments', views.AccountAssignmentList.as_view(), name='account-assignment-list'),
        ])),
        path('list', views.AccountFormList.as_view(), name='account-list'),
        path('credentials', views.AccountCredentials.as_view(), name='account-credentials'),
    ])),
    path('subscription/', include([
        path('create/<str:object_model>/<int:object_id>', views.SubscriptionCreate.as_view(), name='subscription-create'),
        path('<int:pk>/', include([
            path('delete', views.SubscriptionDelete.as_view(), name='subscription-delete'),
        ])),
    ])),
    path('activity/', include([
        path('list', views.ActivityList.as_view(), name='activity-list'),
        path('mark', views.ActivityMark.as_view(), name='activity-mark'),
        path('settings', views.ManageSubscriptions.as_view(), name='activity-settings'),
    ])),
    path('comment/', include([
        path('create', views.CommentCreate.as_view(), name='comment-create'),
        path('<int:pk>/', include([
            path('reply', views.CommentCreate.as_view(), name='comment-reply'),
            path('update', views.CommentUpdate.as_view(), name='comment-update'),
            path('delete', views.CommentDelete.as_view(), name='comment-delete'),
        ])),
    ])),
    path('message/<int:user_id>/create', under_development(views.MessageCreate.as_view()), name='message-create'),
    path('chat/list', under_development(views.ChatList.as_view()), name='chat-list'),
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
    path('mark_activities_as_read', views.mark_activities_as_read, name='mark-activities-as-read'),
    path('mark_notifications_as_read', views.mark_notifications_as_read, name='mark-notifications-as-read'),
    path('notification/', include([
        path('list', views.NotificationList.as_view(), name='notification-list'),
    ])),
]
