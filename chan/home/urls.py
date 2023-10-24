from django.urls import path
from . import views

urlpatterns = [
    path('', views.test, name='index'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
]
