from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    OrderingFilterBackend,
    SearchFilterBackend,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from .documents import ProductDocument
from .serializers import ProductDocumentSerializer

class ProductSearchViewSet(DocumentViewSet):
    document = ProductDocument
    serializer_class = ProductDocumentSerializer
    lookup_field = 'id'
    filter_backends = [
        FilteringFilterBackend,
        OrderingFilterBackend,
        SearchFilterBackend,
    ]
    search_fields = (
        'title',
        'description',
    )
    filter_fields = {
        'price': 'price',
        'condition': 'condition',
    }
    ordering_fields = {
        'title': 'title',
        'price': 'price',
    }
    ordering = ('id',)

  
