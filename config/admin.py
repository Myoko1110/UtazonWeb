from config.models import Item, Sale
from django.contrib import admin


class ItemAdmin(admin.ModelAdmin):
    def change_view(self, request, object_id, form_url="", extra_context=None):
        self.readonly_fields = ('id', 'item_id', 'purchases_number')
        return self.changeform_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url="", extra_context=None):
        self.readonly_fields = ()
        return self.changeform_view(request, None, form_url, extra_context)


class ItemDetailsInline(admin.StackedInline):
    model = Sale
    can_delete = False
    verbose_name = "Item Sale"


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    inlines = (ItemDetailsInline,)

    list_display = ('item_id', 'item_name', 'price')
    exclude = ('id', 'purchases_number')

    def change_view(self, request, object_id, form_url="", extra_context=None):
        self.readonly_fields = ('item_id',)
        return self.changeform_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url="", extra_context=None):
        self.readonly_fields = ()
        return self.changeform_view(request, None, form_url, extra_context)
