# coding: utf-8
from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailadmin.edit_handlers import (
    InlinePanel, FieldPanel, PageChooserPanel)

from catalog.models import Region, Office


class StaticPage(Page):
    body = RichTextField(verbose_name="Текст сторінки")
    template = "cms_pages/static_page.jinja"

    class Meta:
        verbose_name = "Статична сторінка"


StaticPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
]


class RawHTMLPage(Page):
    body = models.TextField(verbose_name="Текст сторінки")
    template = "cms_pages/static_page.jinja"

    class Meta:
        verbose_name = "Raw-HTML сторінка"


class NewsPage(Page):
    lead = RichTextField(verbose_name="Лід", blank=True)
    body = RichTextField(verbose_name="Текст новини")
    date_added = models.DateTimeField(verbose_name="Опубліковано")
    sticky = models.BooleanField(verbose_name="Закріпити новину",
                                 default=False)
    important = models.BooleanField(verbose_name="Важлива новина",
                                    default=False)

    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    template = "cms_pages/news_page.jinja"

    class Meta:
        verbose_name = "Новина"


NewsPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('lead', classname="full"),
    FieldPanel('body', classname="full"),
    FieldPanel('date_added'),
    FieldPanel('sticky'),
    FieldPanel('important'),
    ImageChooserPanel('image'),
]


class NewsIndexPage(Page):
    template = "cms_pages/news_index_page.jinja"

    def get_context(self, request, *args, **kwargs):
        ctx = super(NewsIndexPage, self).get_context(request, *args, **kwargs)

        latest_news = NewsPage.objects.live().order_by(
            "-date_added")

        ctx["latest_news"] = latest_news
        return ctx

    class Meta:
        verbose_name = "Сторінка новин"


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
        related_name='+',
        on_delete=models.CASCADE
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


class HomePageBottomMenuLink(Orderable, LinkFields):
    page = ParentalKey('cms_pages.HomePage', related_name='bottom_menu_links')


class HomePage(Page):
    body = RichTextField(verbose_name="Текст сторінки")
    news_count = models.IntegerField(
        default=6,
        verbose_name="Кількість новин на сторінку")

    template = "cms_pages/home.jinja"

    class Meta:
        verbose_name = "Головна сторінка"


HomePage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
    FieldPanel('news_count'),
    InlinePanel('top_menu_links', label="Меню зверху"),
    InlinePanel('bottom_menu_links', label="Меню знизу"),
]


class MetaData(models.Model):
    region = models.ForeignKey(Region, blank=True, null=True, on_delete=models.SET_NULL)
    office = models.ForeignKey(Office, blank=True, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("region", "office")

    def __unicode__(self):
        chunks = []
        if self.region is not None:
            chunks.append(self.region.region_name)

        if self.office is not None:
            chunks.append(self.office.name)

        return ": ".join(chunks)

    def __str__(self):
        return self.__unicode__()


class PersonMeta(models.Model):
    fullname = models.CharField("Повне ім'я", max_length=150)
    year = models.IntegerField(
        "Рік декларації", blank=True, null=True, choices=(
            (2011, 2011),
            (2012, 2012),
            (2013, 2013),
            (2014, 2014),
            (2015, 2015),))
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("year", "fullname")

    def __unicode__(self):
        chunks = []
        if self.fullname is not None:
            chunks.append(self.fullname)

        if self.year is not None:
            chunks.append(str(self.year))

        return ": ".join(chunks)

    def __str__(self):
        return self.__unicode__()
