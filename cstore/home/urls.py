from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    # path('', views.test, name='index'),
    path('', views.index, name='index'),
    path('update_city/', views.update_city, name='update_city'),
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),
    path('terms-conditions/', views.terms_conditions, name='terms-conditions'),
    path('legal-notice/', views.legal_notice, name='legal-notice'),
   

   
]
