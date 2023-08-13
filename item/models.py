from django.db import models


class Banner(models.Model):
    IMG_TYPES = (
        ("mobile", "Mobile"),
        ("pc", "PC"),
    )
    id = models.AutoField(unique=True, primary_key=True)
    banner_img = models.ImageField(upload_to="banner")
    view_type = models.CharField(max_length=6, choices=IMG_TYPES, default="pc")

    def __str__(self):
        return f"{self.view_type} {self.id} {self.banner_img}"
