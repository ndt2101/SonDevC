from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('user_token', views.user_longterm_token, name='user_token'),
    path('user_pages', views.get_pages, name='user_pages'),
    path('collect_cmts', views.collect_comment_pages, name="collect_cmts"),
    path('predict', views.get_predictions, name="predict")
]