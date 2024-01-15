
from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    # ... other url patterns ...
    path('search/', views.search, name='search'),
]
