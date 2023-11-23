from django.urls import path
from .views import create_company
app_name = 'companies'
urlpatterns = [
    # ... other url patterns ...
    path('create-company/', create_company, name='create_company'),
]
