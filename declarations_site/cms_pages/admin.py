from django.contrib import admin
from cms_pages.models import MetaData, PersonMeta


class MetaDataAdmin(admin.ModelAdmin):
    pass


class PersonMetaAdmin(admin.ModelAdmin):
    list_display = ("pk", "fullname", "year", "title", "description")
    list_editable = ("fullname", "year", "title", "description")


admin.site.register(MetaData, MetaDataAdmin)
admin.site.register(PersonMeta, PersonMetaAdmin)
