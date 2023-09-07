from django.urls import path

from . import views

app_name = 'account'
urlpatterns = [
    path('', views.mypage, name='mypage'),
    path('list_item/', views.list_item, name='list_item'),
    path('on_sale/', views.on_sale, name='on_sale'),
    path('on_sale/edit/', views.item_edit, name='item_edit'),
    path('on_sale/edit/post/', views.item_edit_post, name='item_edit_post'),
]