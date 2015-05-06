from django.contrib import admin
from cms_pages.models import MetaData


class MetaDataAdmin(admin.ModelAdmin):
    pass


admin.site.register(MetaData, MetaDataAdmin)
