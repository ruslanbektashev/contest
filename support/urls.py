from django.urls import path, include

from . import views

app_name = 'support'

urlpatterns = [
    path('', views.Support.as_view(), name='index'),
    path('faq/', include([
        path('create', views.FAQCreate.as_view(), name='faq-create'),
        path('<int:pk>/', include([
            path('', views.FAQDetail.as_view(), name='faq-detail'),
            path('update', views.FAQUpdate.as_view(), name='faq-update'),
            path('delete', views.FAQDelete.as_view(), name='faq-delete')
        ])),
        path('list', views.FAQList.as_view(), name='faq-list'),
    ])),
    path('report/', include([
        path('create/', views.ReportCreateView.as_view(), name='report-create'),
        path('<int:pk>/', include([
            path('', views.ReportDetailView.as_view(), name='report-detail'),
            path('update/', views.ReportUpdateView.as_view(), name='report-update'),
            path('delete/', views.ReportDeleteView.as_view(), name='report-delete')
        ])),
        path('list/', views.ReportListView.as_view(), name='report-list'),
    ])),
]
