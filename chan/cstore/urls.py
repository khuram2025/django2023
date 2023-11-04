from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls', namespace='home')),  # Assuming you have a home app with its own urls
    path('account/', include('account.urls')), 
    path('product/', include('product.urls')),  
]
