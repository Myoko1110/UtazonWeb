from django.urls import path
from . import views

app_name = 'browse'
urlpatterns = [
    path('', views.index_view, name='index'),
    path('item/', views.item, name='item'),
    path('cart/', views.cart, name='cart')
]