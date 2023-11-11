from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductSearchViewSet

router = DefaultRouter()
router.register(r'products', ProductSearchViewSet, basename='productsearch')

urlpatterns = [
    path('', include(router.urls)),
]
