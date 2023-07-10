from django.urls import path
from . import views


app_name = 'item'
urlpatterns = [
    path('', views.index_view, name='index'),
    path('item/', views.item, name='item'),
    path('cart/', views.cart, name='cart'),
    path('cart/delete/', views.cart_delete, name='cart_delete'),
    path('cart/add/', views.cart_add, name='cart_add'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('later/delete/', views.later_delete, name='later_delete'),
    path('cart-to-later/', views.cart_to_later, name='cart_to_later'),
    path('later-to-cart/', views.later_to_cart, name='later_to_cart'),
    path('search/', views.search, name='search'),
    path('review/', views.review, name='review'),
    path('review/post/', views.review_post, name='review_post'),
    path('review/userful/', views.review_userful, name='review_userful'),
]
