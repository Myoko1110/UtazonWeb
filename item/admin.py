from django.contrib import admin

from item.models import Banner, Featured


class BannerAdmin(admin.ModelAdmin):
    def change_view(self, request, object_id, form_url="", extra_context=None):
        self.list_display = ('view_type', 'id', 'banner_img')
        self.readonly_fields = ('id', 'banner_img', 'view_type')
        return self.changeform_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url="", extra_context=None):
        self.list_display = ('view_type', 'id', 'banner_img')
        self.readonly_fields = ()
        return self.changeform_view(request, None, form_url, extra_context)


class FeaturedAdmin(admin.ModelAdmin):
    list_display = ("title",)


admin.site.register(Banner, BannerAdmin)
admin.site.register(Featured, FeaturedAdmin)
