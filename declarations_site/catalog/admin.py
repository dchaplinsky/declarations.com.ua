from django.contrib import admin
from catalog.models import Region


class RegionAdmin(admin.ModelAdmin):
    list_display = ("region_name", "region_name_en", "order_id", )
    list_editable = ("region_name_en", "order_id", )


admin.site.register(Region, RegionAdmin)

