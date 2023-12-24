from django.urls import path

from . import views

app_name = 'pride'
urlpatterns = [
    path('', views.pride, name="pride"),
    path('register/', views.register, name="register"),
    path('register/confirm/', views.register_confirm, name="register_confirm")
]
