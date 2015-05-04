# coding: utf-8
from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailadmin.edit_handlers import (
    InlinePanel, FieldPanel, PageChooserPanel)


class StaticPage(Page):
    body = RichTextField(verbose_name="Текст сторінки")
    template = "cms_pages/static_page.jinja"

    def get_context(self, request, *args, **kwargs):
        return {
            'page': self,
            'request': request,
        }

    class Meta:
        verbose_name = "Статична сторінка"

StaticPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
]


class RawHTMLPage(Page):
    body = models.TextField(verbose_name="Текст сторінки")
    template = "cms_pages/static_page.jinja"

    def get_context(self, request, *args, **kwargs):
        return {
            'page': self,
            'request': request,
        }

    class Meta:
        verbose_name = "Raw-HTML сторінка"

RawHTMLPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
]


class LinkFields(models.Model):
    caption = models.CharField(max_length=255, blank=True)

    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        else:
            return self.link_external

    panels = [
        FieldPanel('caption'),
        FieldPanel('link_external'),
        PageChooserPanel('link_page')
    ]

    class Meta:
        abstract = True


class HomePageTopMenuLink(Orderable, LinkFields):
    page = ParentalKey('cms_pages.HomePage', related_name='top_menu_links')


class HomePage(Page):
    body = RichTextField(verbose_name="Текст сторінки")

    template = "cms_pages/home.jinja"

    def get_context(self, request, *args, **kwargs):
        return {
            'page': self,
            'request': request,
        }

    class Meta:
        verbose_name = "Головна сторінка"

HomePage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
    InlinePanel(HomePage, 'top_menu_links', label="Меню зверху"),
]
