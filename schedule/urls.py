from django.urls import path, include

from schedule import views

app_name = 'schedule'

urlpatterns = [
    path('create', views.ScheduleCreate.as_view(), name='schedule-create'),
    path('<int:pk>/', include([
        path('', views.ScheduleDetail.as_view(), name='schedule-detail'),
        path('delete', views.ScheduleDelete.as_view(), name='schedule-delete'),
    ])),
    path('list', views.ScheduleList.as_view(), name='schedule-list'),
    path('attachment/<int:pk>', views.ScheduleAttachmentDetail.as_view(), name='scheduleattachment-detail'),
]
