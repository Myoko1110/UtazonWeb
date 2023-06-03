from django.urls import path
from . import views

app_name = 'browse'
urlpatterns = [
    path('', views.IndexView, name='index'),
    path('item/', views.Item, name='item'),
]