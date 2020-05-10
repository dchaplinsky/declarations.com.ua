from django.contrib import admin
from django import forms
from .models import LandingPage, Person, Declaration
from django.utils.html import format_html
from django.template.loader import render_to_string
import nested_admin


class AddLandingPageForm(forms.ModelForm):
    bulk_list = forms.CharField(
        label="Перелік персон для лендінг-сторінки (одна особа у рядку)",
        widget=forms.Textarea,
    )

    class Meta:
        model = LandingPage
        fields = "__all__"


class DeclarationInline(nested_admin.NestedTabularInline):
    model = Declaration
    extra = 0
    max_num = 0
    fields = ("declaration_snippet", "year", "corrected", "user_declarant_id", "exclude")
    readonly_fields = ("declaration_snippet", "year", "corrected", "user_declarant_id")
    ordering = ("user_declarant_id", "year")


    def declaration_snippet(self, obj):
        return render_to_string("admin/decls_snippet.jinja", {"d": obj})

    declaration_snippet.short_description = "Картка декларації"


class PersonInline(nested_admin.NestedTabularInline):
    model = Person
    extra = 1
    fields = ("name", "extra_keywords")
    inlines = [DeclarationInline]


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("declarations")


class LandingPageAdmin(nested_admin.NestedModelAdmin):
    inlines = [PersonInline]

    list_display = ("slug", "title", "keywords", "members", "region", "body_type")
    list_filter = ("region", "body_type")

    def members(self, obj):
        return obj.persons.count()

    def get_form(self, request, obj=None, **kwargs):
        if obj is not None:
            return super().get_form(request, obj, **kwargs)
        else:
            return AddLandingPageForm

    def save_model(self, request, obj, form, change):
        res = super().save_model(request, obj, form, change)

        if not change:
            persons = list(
                filter(None, map(str.strip, form.cleaned_data["bulk_list"].split("\n")))
            )
            for name in persons:
                p = Person.objects.create(body=obj, name=name)

        obj.pull_declarations()
        return res


admin.site.register(LandingPage, LandingPageAdmin)
