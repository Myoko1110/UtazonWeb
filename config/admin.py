from config.models import Item
from django.contrib import admin


class ItemAdmin(admin.ModelAdmin):
    def change_view(self, request, object_id, form_url="", extra_context=None):
        self.list_display = ('item_id', 'item_name', 'price')
        self.readonly_fields = ('id', 'item_id', 'purchases_number')
        return self.changeform_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url="", extra_context=None):
        self.list_display = ('item_id', 'item_name', 'price')
        self.readonly_fields = ()
        return self.changeform_view(request, None, form_url, extra_context)


admin.site.register(Item, ItemAdmin)
