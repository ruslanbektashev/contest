from django.urls import path, include

from contest.utils import under_development
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
            path('discussion', views.CourseDiscussion.as_view(), name='course-discussion'),
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
    path('filter/', include([
        path('<int:user_id>/<int:course_id>/create', views.FilterCreate.as_view(), name='filter-create'),
        path('<int:pk>/delete', views.FilterDelete.as_view(), name='filter-delete'),
        path('table', views.FilterTable.as_view(), name='filter-table')
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
            path('discussion', views.ContestDiscussion.as_view(), name='contest-discussion'),
            path('attachment/<int:attachment_id>', views.ContestAttachment.as_view(), name='contest-attachment'),
            path('update', views.ContestUpdate.as_view(), name='contest-update'),
            path('delete', views.ContestDelete.as_view(), name='contest-delete')
        ]))
    ])),
    path('contest/<int:contest_id>/problem/create/<str:type>', views.ProblemCreate.as_view(), name='problem-create'),
    path('problem/', include([
        path('<int:pk>/', include([
            path('', views.ProblemDetail.as_view(), name='problem-detail'),
            path('rollback', views.ProblemRollbackResults.as_view(), name='problem-rollback-results'),
            path('discussion', views.ProblemDiscussion.as_view(), name='problem-discussion'),
            path('attachment/<int:attachment_id>', views.ProblemAttachment.as_view(), name='problem-attachment'),
            path('update', views.ProblemUpdate.as_view(), name='problem-update'),
            path('delete', views.ProblemDelete.as_view(), name='problem-delete')
        ]))
    ])),
    path('problem/<int:problem_id>/submission/pattern/create', views.SubmissionPatternCreate.as_view(), name='submission-pattern-create'),
    path('submission/pattern/', include([
        path('<int:pk>/', include([
            path('', views.SubmissionPatternDetail.as_view(), name='submission-pattern-detail'),
            path('update', views.SubmissionPatternUpdate.as_view(), name='submission-pattern-update'),
            path('delete', views.SubmissionPatternDelete.as_view(), name='submission-pattern-delete')
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
            path('attachment/<int:attachment_id>', views.UTTestAttachment.as_view(), name='uttest-attachment'),
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
            path('discussion', views.AssignmentDiscussion.as_view(), name='assignment-discussion'),
            path('update', views.AssignmentUpdate.as_view(), name='assignment-update'),
            path('delete', views.AssignmentDelete.as_view(), name='assignment-delete')
        ])),
        path('list', views.AssignmentUserTable.as_view(), name='assignment-list')
    ])),
    path('course/<int:course_id>/submission/list', views.SubmissionList.as_view(), name='submission-list'),
    path('course/<int:course_id>/submission/backup', views.SubmissionBackup.as_view(), name='submission-backup'),
    path('problem/<int:problem_id>/submission/create', views.SubmissionCreate.as_view(), name='submission-create'),
    path('problem/<int:problem_id>/submission/<int:submission_id>/continue', views.SubmissionCreate.as_view(), name='submission-continue'),
    path('submission/', include([
        path('<int:pk>/', include([
            path('', views.SubmissionDetail.as_view(), name='submission-detail'),
            path('update', views.SubmissionUpdate.as_view(), name='submission-update'),
            path('delete', views.SubmissionDelete.as_view(), name='submission-delete'),
            path('evaluate', views.SubmissionEvaluate.as_view(), name='submission-evaluate'),
            path('clear_task', views.SubmissionClearTask.as_view(), name='submission-clear-task'),
            path('moss', views.SubmissionMoss.as_view(), name='submission-moss'),
            path('download', views.SubmissionDownload.as_view(), name='submission-download'),
            path('attachment/<int:attachment_id>', views.SubmissionAttachment.as_view(), name='submission-attachment'),
            path('get_executions', views.ExecutionList.as_view(), name='submission-get-executions'),
        ])),
        path('get_progress/<str:task_id>', views.submission_get_progress, name='submission-get-progress'),
        path('list', views.SubmissionList.as_view(), name='submission-list'),
    ])),
    path('event/', include([
        path('create', under_development(views.EventCreate.as_view()), name='event-create'),
        path('<int:pk>/', include([
            path('', under_development(views.EventDetail.as_view()), name='event-detail'),
            path('update', under_development(views.EventUpdate.as_view()), name='event-update'),
            path('delete', under_development(views.EventDelete.as_view()), name='event-delete')
        ])),
        path('schedule', under_development(views.EventSchedule.as_view()), name='event-schedule')
    ])),
    path('contest/<int:contest_id>/test/create', views.TestCreate.as_view(), name='test-create'),
    path('contest/<int:contest_id>/question/create', views.QuestionCreate.as_view(), name='question-create'),
    path('test/<int:test_id>/testsubmission/create', views.TestSubmissionRedirect.as_view(), name='testsubmission-create'),
    path('test/<int:test_id>/questions/add', views.AddQuestions.as_view(), name='questions-add'),
    path('test/', include([
        path('<int:pk>/', include([
            path('', views.TestDetail.as_view(), name='test-detail'),
            path('update', views.TestUpdate.as_view(), name='test-update'),
            path('delete', views.TestDelete.as_view(), name='test-delete'),
        ]))
    ])),
    path('contest/<int:contest_id>/test/<int:test_id>/question/create', views.QuestionCreate.as_view(), name='question-in-test-create'),
    path('question/<int:question_id>/option/create', views.OptionCreate.as_view(), name='option-create'),
    path('question/', include([
        path('<int:pk>/', include([
            path('', views.QuestionDetail.as_view(), name='question-detail'),
            path('update', views.QuestionUpdate.as_view(), name='question-update'),
            path('delete', views.QuestionDelete.as_view(), name='question-delete'),
        ]))
    ])),
    path('option/', include([
        path('<int:pk>/', include([
            path('update', views.OptionUpdate.as_view(), name='option-update'),
            path('delete', views.OptionDelete.as_view(), name='option-delete'),
        ]))
    ])),
    path('test/<int:test_id>/testsubmission/create', views.TestSubmissionRedirect.as_view(), name='testsubmission-create'),
    path('testsubmission/<int:testsubmission_id>/answer/create', views.AnswerInTestSubmissionCreate.as_view(), name='answer-in-testsubmission-create'),
    path('testsubmission/', include([
        path('<int:pk>/', include([
            path('', views.TestSubmissionDetail.as_view(), name='testsubmission-detail'),
        ]))
    ])),
    path('question/<int:question_id>/answer/create', views.AnswerCreate.as_view(), name='answer-create'),
    path('answer/', include([
        path('<int:pk>/', include([
            path('', views.AnswerDetail.as_view(), name='answer-detail'),
            path('check', views.AnswerCheck.as_view(), name='answer-check'),
        ]))
    ])),
    path('testmembership/', include([
        path('<int:pk>/', include([
            path('update', views.TestMembershipUpdate.as_view(), name='testmembership-update'),
            path('delete', views.TestMembershipDelete.as_view(), name='testmembership-delete'),
        ])),
    ])),
]
