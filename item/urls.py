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
    path('review/helpful/', views.helpful, name='review_helpful'),
    path('review/star/', views.review_star, name='review_star'),
    path('review/edit/', views.review_edit, name='review_edit'),
    path('review/edit/post/', views.review_edit_post, name='review_edit_post'),
    path('category/', views.category, name='category'),
    path('history/', views.history, name='history'),
    path('browsing-history/', views.browsing_history, name='browsing_history'),
    path('history/status/', views.status, name='status'),
    path('suggest/', views.suggest, name='suggest'),
    path('initialize_browsing_history/', views.initialize_browsing_history, name='initialize_browsing_history'),
    path('update_browsing_history/', views.update_browsing_history, name='update_browsing_history'),
]
