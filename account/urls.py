from django.urls import path

from . import views

app_name = 'account'
urlpatterns = [
    path('', views.mypage, name='mypage'),
    path('list_item/', views.list_item, name='list_item'),
    path('list_item/post/', views.list_item_post, name='list_item_post'),
    path('available/', views.available, name='available'),
    path('available/edit/', views.item_edit, name='item_edit'),
    path('available/edit/post/', views.item_edit_post, name='item_edit_post'),
    path('available/stock/', views.item_stock, name='item_stock'),
    path('available/stock/post/', views.item_stock_post, name='item_stock_post'),
    path('available/delete/', views.item_delete, name='item_delete'),
    path('available/return/', views.item_return, name='item_return'),
    path('available/return/post/', views.item_return_post, name='item_return_post'),
    path('unavailable/', views.unavailable, name='unavailable'),
]
