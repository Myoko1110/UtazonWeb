from django.urls import path
from . import views

app_name = 'buy'
urlpatterns = [
    path('', views.buy, name='index'),

]