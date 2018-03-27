from django.urls import path

from . import views

app_name = 'woodcutter'
urlpatterns = [
    path('', views.main, name='index'),
    path('input', views.inputFields, name='inputform'),
    path('submit', views.submit, name='submit'),
    path('errorlist', views.error_list, name='errorlist'),
    path('editlog', views.edit_log, name='editlog'),
    path('<int:game_id>/display/', views.display, name='display'),
]
