from django.urls import path
from . import views

app_name = 'buy'
urlpatterns = [
    path('', views.buy, name='buy'),
    path('confirm/', views.buy_confirm, name='buy_confirm'),

]