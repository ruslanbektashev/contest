from django.urls import include, path

from accounts import api, views

app_name = 'accounts'

urlpatterns = [
    path('group/', include([
        path('<int:pk>/', include([
            path('', views.GroupDetail.as_view(), name='group-detail'),
            path('update', views.GroupUpdate.as_view(), name='group-update'),
        ])),
    ])),
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
    path('notification/', include([
        path('list', views.NotificationList.as_view(), name='notification-list'),
        path('read', views.NotificationMarkAllAsRead.as_view(), name='notification-mark-all-as-read'),
        path('delete', views.NotificationDeleteRead.as_view(), name='notification-mark-read-as-deleted'),
    ])),
    path('comment/', include([
        path('create', views.CommentCreate.as_view(), name='comment-create'),
        path('<int:pk>/', include([
            path('reply', views.CommentCreate.as_view(), name='comment-reply'),
            path('update', views.CommentUpdate.as_view(), name='comment-update'),
            path('delete', views.CommentDelete.as_view(), name='comment-delete'),
        ])),
    ])),
    path('announcement/', include([
        path('create', views.AnnouncementCreate.as_view(), name='announcement-create'),
        path('<int:pk>/', include([
            path('', views.AnnouncementDetail.as_view(), name='announcement-detail'),
            path('update', views.AnnouncementUpdate.as_view(), name='announcement-update'),
            path('delete', views.AnnouncementDelete.as_view(), name='announcement-delete')
        ])),
        path('list', views.AnnouncementList.as_view(), name='announcement-list'),
    ])),
] + [
    path('api/', include([
        path('comment/mark', api.CommentMarkAsReadAPI.as_view(), name='api-comment-mark-as-read'),
        path('notification/mark', api.NotificationMarkAsReadAPI.as_view(), name='api-notification-mark-as-read'),
    ]))
]
