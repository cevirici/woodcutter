from django.urls import path

from . import views

app_name = 'woodcutter'
urlpatterns = [
    path('', views.main, name='index'),
    path('input', views.inputFields, name='inputform'),
    path('submit', views.submit, name='submit'),
    path('<int:game_id>/display/', views.display, name='display'),
]