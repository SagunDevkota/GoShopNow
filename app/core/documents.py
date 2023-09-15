from django_elasticsearch_dsl import Document,Index,fields

from core.models import Product,Category,ProductImage

product_index = Index('product')
product_index.settings(
    number_of_shards = 1,
    number_of_replicas = 1,
)
   

@product_index.doc_type
class ProductDocument(Document):
    """Product document for elastic search."""
    p_id = fields.IntegerField(attr='p_id')
    name = fields.TextField(
        fields = {
            "raw":{
                "type":"keyword"
            }
        }
    )
    price = fields.FloatField(attr='price')
    threshold = fields.IntegerField(attr='threshold')
    stock = fields.IntegerField(attr='stock')
    rating = fields.FloatField(attr='rating')
    category = fields.TextField(attr='category.category')
    image_url = fields.TextField(attr='image_url.url')
    class Django(object):
        model = Product
        related_models = [Category, ProductImage]

    def prepare_image_url(self, instance):
        if instance.product_id_image:
            if instance.product_id_image.first():
                return instance.product_id_image.first().image_url.url
        return ''

    def get_queryset(self):
        """Not mandatory but to improve performance we can select related in one sql request"""
        return super(ProductDocument, self).get_queryset().select_related(
            'category'
        )

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Product instance(s) from the related model.
        The related_models option should be used with caution because it can lead in the index
        to the updating of a lot of items.
        """
        # if isinstance(related_instance, Category):
        #     return related_instance.pk
        # el
        if isinstance(related_instance, ProductImage):
            return related_instance.p_id
    

