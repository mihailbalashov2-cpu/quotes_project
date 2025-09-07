from django.urls import path
from . import views

urlpatterns = [
    path('', views.random_quote_view, name='random_quote'),
    path('add/', views.add_quote_view, name='add_quote'),
    path('top/', views.top_quotes_view, name='top_quotes'),
    path('all/', views.all_quotes_view, name='all_quotes'),
    path('all/filter/', views.filter_quotes_ajax, name='filter_quotes_ajax'),
    path('api/quote/<int:quote_id>/like/', views.like_quote_api, name='like_quote_api'),
]
