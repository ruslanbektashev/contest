from django.urls import path, include

from . import views

app_name = 'support'

urlpatterns = [
    path('faq/', include([
        path('create', views.FAQCreate.as_view(), name='faq-create'),
        path('<int:pk>/', include([
            path('', views.FAQDetail.as_view(), name='faq-detail'),
            path('update', views.FAQUpdate.as_view(), name='faq-update'),
            path('delete', views.FAQDelete.as_view(), name='faq-delete')
        ])),
        path('list', views.FAQList.as_view(), name='faq-list'),
    ])),
]