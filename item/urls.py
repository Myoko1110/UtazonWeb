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
    path('review/', views.review, name='review'),
    path('review/post/', views.review_post, name='review_post'),
    path('review/userful/', views.review_userful, name='review_userful'),
]