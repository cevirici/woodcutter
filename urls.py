from django.urls import path

from . import views

app_name = 'woodcutter'
urlpatterns = [
    path('', views.main, name='index'),
    path('input', views.inputFields, name='inputform'),
    path('submit', views.submit, name='submit'),
    path('errorlist', views.error_list, name='errorlist'),
    path('forceerrorlist', views.force_error_list, name='forceerrorlist'),
    path('editlog', views.edit_log, name='editlog'),
    path('random', views.random, name='random'),
    path('mpass', views.isMPassIn, name='hacky'),
    path('<int:game_id>/display/', views.display, name='display'),
]
