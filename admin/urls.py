from django.urls import path

from . import views

app_name = "admin"
urlpatterns = [
    path('', views.admin_index),
    path('items/', views.admin_items),
    path('items/get/', views.admin_items_get),
    path('items/stop/', views.admin_items_stop),
    path('items/sale/end/', views.admin_items_end_sale),
    path('items/sale/set/', views.admin_items_set_sale),
    path("login/", views.admin_login),
    path("logout/", views.admin_logout),
]
