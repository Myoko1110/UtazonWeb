from django.db import models


class Item(models.Model):
    id = models.IntegerField(primary_key=True)
    item_id = models.IntegerField(unique=True)
    item_name = models.CharField(max_length=256)
    price = models.FloatField()
    image = models.JSONField()
    review = models.JSONField()
    stock = models.BigIntegerField(),
    kind = models.JSONField(),
    category = models.CharField(64),
    purchases_number = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'utazon_item'

    def __str__(self):
        return f"{self.item_name}"
