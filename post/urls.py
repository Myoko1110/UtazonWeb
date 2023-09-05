from django.urls import path

from . import views

app_name = 'post'
urlpatterns = [
    path('order_list', views.order_list, name='order_list'),
    path('mailbox_full', views.mailbox_full, name='mailbox_full'),
    path('mailbox_notfound', views.mailbox_notfound, name='mailbox_notfound'),
]
