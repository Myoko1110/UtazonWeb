from django.urls import path
from . import views

app_name = 'browse'
urlpatterns = [
    path('', views.index_view, name='index'),
    path('item/', views.item, name='item'),
    path('cart/', views.cart, name='cart'),
    path('cart/delete/', views.cart_delete, name='cart_delete'),
    path('cart/add/', views.cart_add, name='cart_add'),
    path('search/', views.search, name='search'),
]