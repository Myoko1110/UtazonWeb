from django.urls import path

from . import views

app_name = 'post'
urlpatterns = [
    path('mailbox_full/', views.mailbox_full, name='mailbox_full'),
    path('mailbox_notfound/', views.mailbox_notfound, name='mailbox_notfound'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('returnstock/item_notfound/', views.returnstock_item_notfound, name='returnstock_item_notfound'),
    path('returnstock/mailbox_full/', views.returnstock_mailbox_full, name='returnstock_mailbox_full'),
    path('returnstock/mailbox_notfound/', views.returnstock_mailbox_notfound, name='returnstock_mailbox_notfound'),
    path('returnstock_complete/', views.returnstock_complete, name='returnstock_complete'),
    path('ship_complete/', views.ship_complete, name='ship_complete'),
    path('upload/', views.upload_detail_img, name='upload_detail_img'),
]
