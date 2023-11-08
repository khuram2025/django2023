from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    # path('', views.test, name='index'),
    path('', views.index, name='index'),
   
]
