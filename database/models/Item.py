from django.db import models


class Item(models.Model):
    sale_id = models.AutoField(unique=True)
    item_id = models.BigIntegerField(unique=True)
    item_name = models.CharField(max_length=256)
    price = models.FloatField()
    image = models.JSONField()
    kind = models.JSONField()
    detail = models.CharField(max_length=10000)
    category = models.CharField(max_length=64)
    purchases_number = models.BigIntegerField()
    mc_uuid = models.UUIDField(max_length=36)
    search_keyword = models.JSONField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    status = models.BooleanField()
