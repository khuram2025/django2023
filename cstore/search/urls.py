from django.urls import path
from .views import search_view

app_name = 'search'


urlpatterns = [
    # ... other URL patterns ...
    path('search/', search_view, name='search'),
]
