from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from product.models import Product, ProductImage

@registry.register_document
class ProductDocument(Document):
    images = fields.ObjectField(properties={
        'image': fields.FileField(attr='image_url')
    })

    def prepare_images(self, instance):
        return [{'image': img.image.url} for img in instance.images.all()]

    class Index:
        name = 'products'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Product
        fields = ['title', 'description', 'price', 'created_at']
        related_models = [ProductImage]
