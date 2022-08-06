from django.db import models
# This is provided by django to create generic relationships
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create a customer manager


class TaggedItemManager(models.Manager):
    def get_by_model(self, obj_type, obj_id):
        """
            Get all the tags for a particular model.
        """
        content_type = ContentType.objects.get_for_model(obj_type)

        queryset = TaggedItem.objects \
            .select_related('tag') \
            .filter(
                content_type=content_type,
                object_id=obj_id
            )
        return queryset

# Create your models here.


class Tag(models.Model):
    label = models.CharField(max_length=255)


class TaggedItem(models.Model):
    # What tag applied to what object
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    # You do not want to import Product from the store app because then the Tag app will be dependent on the store app.
    # Intead you want to use a generic object. A tag can be applied to product, or video, article or whatever.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # This is needed so that we can point to the primary key of the generic object
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
