from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls', namespace='home')),  # Assuming you have a home app with its own urls
    path('account/', include('account.urls')), 
    path('product/', include('product.urls')),  
    path('search/', include('search.urls')),
    path('companies/', include('companies.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
