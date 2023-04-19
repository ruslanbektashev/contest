from django.urls import include, path

from support import api, views

app_name = 'support'

urlpatterns = [
    path('', views.Support.as_view(), name='index'),
    path('question/', include([
        path('create', views.QuestionCreate.as_view(), name='question-create'),
        path('<int:pk>/', include([
            path('', views.QuestionDetail.as_view(), name='question-detail'),
            path('update', views.QuestionUpdate.as_view(), name='question-update'),
            path('delete', views.QuestionDelete.as_view(), name='question-delete')
        ])),
        path('list', views.QuestionList.as_view(), name='question-list'),
    ])),
    path('report/', include([
        path('create/', views.ReportCreate.as_view(), name='report-create'),
        path('<int:pk>/', include([
            path('', views.ReportDetail.as_view(), name='report-detail'),
            path('update/', views.ReportUpdate.as_view(), name='report-update'),
            path('delete/', views.ReportDelete.as_view(), name='report-delete')
        ])),
        path('list/', views.ReportList.as_view(), name='report-list'),
    ])),
    path('discussion/<int:pk>/', views.DiscussionDetail.as_view(), name='discussion-detail'),
    path('change/list', views.ChangeList.as_view(), name='change-list'),
    path('tutorial/reset/<str:view>/', views.TutorialReset.as_view(), name='tutorial-reset'),
] + [
    path('api/', include([
        path('tutorial/step/pass/', api.TutorialStepPassCreateAPI.as_view(), name='api-tutorial-step-pass-create')
    ]))
]
