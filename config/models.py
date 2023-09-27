from django.db import models


class Item(models.Model):
    sale_id = models.AutoField(primary_key=True)
    item_id = models.BigIntegerField()
    item_name = models.CharField(max_length=256)
    price = models.FloatField()
    image = models.JSONField(null=True, blank=True)
    review = models.JSONField(null=True, blank=True)
    stock = models.BigIntegerField(null=True, blank=True),
    kind = models.JSONField(null=True, blank=True),
    category = models.CharField(max_length=64),
    purchases_number = models.BigIntegerField(default=0, null=True, blank=True)
    mc_uuid = models.CharField(max_length=36)
    search_keyword = models.JSONField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'utazon_item'

    def get_sale_info(self):
        try:
            sale_info = Sale.objects.get(item_id=self.item_id)
            return sale_info
        except Sale.DoesNotExist:
            return None

    def __str__(self):
        return f"{self.item_name}"


class Sale(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    item_id = models.OneToOneField(Item, on_delete=models.CASCADE, db_column='item_id')
    sale_status = models.BooleanField(default=False)
    discount_rate = models.IntegerField()
    sale_start = models.DateTimeField()
    sale_end = models.DateTimeField()

    class Meta:
        db_table = 'utazon_sale'

    def __str__(self):
        return f"{self.item_id}"
