from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Product

@registry.register_document
class ProductDocument(Document):
    class Index:
        # Name of the Elasticsearch index
        name = 'products'
        # See Elasticsearch documentation for more settings

    class Django:
        model = Product  # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'title',
            'description',
            'price',
            # Add other fields you want to index and search
        ]

        # For foreign key fields, you can use related fields
        related_models = ['product.Category', 'locations.City', 'companies.CompanyProfile']
    
    # Example of how to index a foreign key field
    category = fields.ObjectField(properties={
        'name': fields.TextField(),
    })

    # Add other methods and fields as needed
