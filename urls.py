from django.urls import path
from django.conf.urls import handler404, handler500

from . import views

app_name = 'woodcutter'
urlpatterns = [
    path('', views.main, name='index'),
    path('input', views.inputFields, name='inputform'),
    path('submit', views.submit, name='submit'),
    path('<int:game_id>/display/', views.display, name='display'),
]

handler404 = views.error_404
handler500 = views.error_500
