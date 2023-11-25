from django.urls import path
from . import views
from account.views import user_profile

app_name = 'companies'
urlpatterns = [
    # ... other url patterns ...
    path('create-company/', views.create_company, name='create_company'),
    path('company/', views.company_detail, name='company_detail'),
    
]
