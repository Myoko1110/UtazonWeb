from django.urls import path

from . import views

app_name = 'account'
urlpatterns = [
    path('', views.mypage, name='mypage'),
    path('list_item/', views.list_item, name='list_item'),
    path('list_item/post/', views.list_item_post, name='list_item_post'),
    path('on_sale/', views.on_sale, name='on_sale'),
    path('on_sale/edit/', views.item_edit, name='item_edit'),
    path('on_sale/edit/post/', views.item_edit_post, name='item_edit_post'),
    path('on_sale/stock/', views.item_stock, name='item_stock'),
    path('on_sale/stock/post/', views.item_stock_post, name='item_stock_post'),
]
