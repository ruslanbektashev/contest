from django.urls import path, include

from contests import views

app_name = 'contests'

urlpatterns = [
    path('', views.index, name='index'),
    path('attachment/<int:pk>/delete', views.AttachmentDelete.as_view(), name='attachment-delete'),
    path('course/<int:course_id>/start', views.CourseStart.as_view(), name='course-start'),
    path('course/', include([
        path('create', views.CourseCreate.as_view(), name='course-create'),
        path('<int:pk>/', include([
            path('', views.CourseDetail.as_view(), name='course-detail'),
            path('update', views.CourseUpdate.as_view(), name='course-update'),
            path('delete', views.CourseDelete.as_view(), name='course-delete')
        ])),
        path('list', views.CourseList.as_view(), name='course-list')
    ])),
    path('credit/', include([
        path('<int:pk>/', include([
            path('update', views.CreditUpdate.as_view(), name='credit-update'),
            path('delete', views.CreditDelete.as_view(), name='credit-delete')
        ]))
    ])),
    path('course/<int:course_id>/lecture/create', views.LectureCreate.as_view(), name='lecture-create'),
    path('lecture/', include([
        path('<int:pk>/', include([
            path('', views.LectureDetail.as_view(), name='lecture-detail'),
            path('update', views.LectureUpdate.as_view(), name='lecture-update'),
            path('delete', views.LectureDelete.as_view(), name='lecture-delete')
        ]))
    ])),
    path('course/<int:course_id>/contest/create', views.ContestCreate.as_view(), name='contest-create'),
    path('contest/', include([
        path('<int:pk>/', include([
            path('', views.ContestDetail.as_view(), name='contest-detail'),
            path('update', views.ContestUpdate.as_view(), name='contest-update'),
            path('delete', views.ContestDelete.as_view(), name='contest-delete')
        ]))
    ])),
    path('contest/<int:contest_id>/problem/create', views.ProblemCreate.as_view(), name='problem-create'),
    path('problem/', include([
        path('<int:pk>/', include([
            path('', views.ProblemDetail.as_view(), name='problem-detail'),
            path('update', views.ProblemUpdate.as_view(), name='problem-update'),
            path('delete', views.ProblemDelete.as_view(), name='problem-delete')
        ]))
    ])),
    path('problem/<int:problem_id>/solution/create', views.SolutionCreate.as_view(), name='solution-create'),
    path('solution/', include([
        path('<int:pk>/', include([
            path('', views.SolutionDetail.as_view(), name='solution-detail'),
            path('update', views.SolutionUpdate.as_view(), name='solution-update'),
            path('delete', views.SolutionDelete.as_view(), name='solution-delete')
        ]))
    ])),
    path('problem/<int:problem_id>/iotest/create', views.IOTestCreate.as_view(), name='iotest-create'),
    path('iotest/', include([
        path('<int:pk>/', include([
            path('', views.IOTestDetail.as_view(), name='iotest-detail'),
            path('update', views.IOTestUpdate.as_view(), name='iotest-update'),
            path('delete', views.IOTestDelete.as_view(), name='iotest-delete')
        ]))
    ])),
    path('problem/<int:problem_id>/uttest/create', views.UTTestCreate.as_view(), name='uttest-create'),
    path('uttest/', include([
        path('<int:pk>/', include([
            path('', views.UTTestDetail.as_view(), name='uttest-detail'),
            path('update', views.UTTestUpdate.as_view(), name='uttest-update'),
            path('delete', views.UTTestDelete.as_view(), name='uttest-delete')
        ]))
    ])),
    path('problem/<int:problem_id>/fntest/create', views.FNTestCreate.as_view(), name='fntest-create'),
    path('fntest/', include([
        path('<int:pk>/', include([
            path('', views.FNTestDetail.as_view(), name='fntest-detail'),
            path('update', views.FNTestUpdate.as_view(), name='fntest-update'),
            path('delete', views.FNTestDelete.as_view(), name='fntest-delete')
        ]))
    ])),
    path('course/<int:course_id>/assignment/', include([
            path('create', views.AssignmentCreate.as_view(), name='assignment-create'),
            path('randomize', views.AssignmentCreateRandomSet.as_view(), name='assignment-randomize'),
            path('table', views.AssignmentCourseTable.as_view(), name='assignment-table')
        ])),
    path('assignment/', include([
        path('<int:pk>/', include([
            path('', views.AssignmentDetail.as_view(), name='assignment-detail'),
            path('update', views.AssignmentUpdate.as_view(), name='assignment-update'),
            path('delete', views.AssignmentDelete.as_view(), name='assignment-delete')
        ])),
        path('list', views.AssignmentUserTable.as_view(), name='assignment-list')
    ])),
    path('problem/<int:problem_id>/submission/create', views.SubmissionCreate.as_view(), name='submission-create'),
    path('submission/', include([
        path('<int:pk>/', include([
            path('', views.SubmissionDetail.as_view(), name='submission-detail'),
            path('delete', views.SubmissionDelete.as_view(), name='submission-delete'),
            path('evaluate', views.SubmissionEvaluate.as_view(), name='submission-evaluate'),
            path('download', views.SubmissionDownload.as_view(), name='submission-download'),
            path('get_executions', views.ExecutionList.as_view(), name='submission-get-executions'),
        ])),
        path('get_progress/<str:task_id>', views.submission_get_progress, name='submission-get-progress'),
        path('list', views.SubmissionList.as_view(), name='submission-list')
    ])),
    path('event/', include([
        path('create', views.EventCreate.as_view(), name='event-create'),
        path('<int:pk>/', include([
            path('', views.EventDetail.as_view(), name='event-detail'),
            path('update', views.EventUpdate.as_view(), name='event-update'),
            path('delete', views.EventDelete.as_view(), name='event-delete')
        ])),
        path('schedule', views.EventSchedule.as_view(), name='event-schedule')
    ]))
]
