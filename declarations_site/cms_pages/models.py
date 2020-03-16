# coding: utf-8
from django.db import models
from django.utils.translation import get_language

from modelcluster.fields import ParentalKey

from wagtail.core.fields import RichTextField
from wagtail.core.models import Page, Orderable
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.edit_handlers import InlinePanel, FieldPanel, PageChooserPanel

from catalog.models import Region, Office
from catalog.utils import TranslatedField, orig_translate_url


class StaticPage(Page):
    title_en = models.CharField(
        verbose_name="[EN] Заголовок",
        max_length=255
    )

    body = RichTextField(verbose_name="[UA] Текст сторінки")
    body_en = RichTextField(verbose_name="[EN] Текст сторінки")
    template = "cms_pages/static_page.jinja"

    class Meta:
        verbose_name = "Статична сторінка"


StaticPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('title_en', classname="full title"),
    FieldPanel('body', classname="full"),
    FieldPanel('body_en', classname="full"),
]


class RawHTMLPage(Page):
    title_en = models.CharField(
        verbose_name="[EN] Заголовок",
        max_length=255
    )

    body = models.TextField(verbose_name="[UA] Текст сторінки")
    body_en = models.TextField(verbose_name="[EN] Текст сторінки")
    template = "cms_pages/static_page.jinja"

    class Meta:
        verbose_name = "Raw-HTML сторінка"


RawHTMLPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('title_en', classname="full title"),
    FieldPanel('body', classname="full"),
    FieldPanel('body_en', classname="full"),
]


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


class LinkFields(models.Model):
    caption = models.CharField(max_length=255, blank=True)
    caption_en = models.CharField(max_length=255, blank=True)

    translated_caption = TranslatedField(
        'caption',
        'caption_en',
    )

    link_external = models.CharField("External link", blank=True, max_length=255)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.CASCADE
    )

    extra_class = models.CharField(max_length=255, blank=True)

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        else:
            if "declarations.com.ua" not in self.link_external:
                return self.link_external

            language = get_language()
            return orig_translate_url(self.link_external, language, "uk")

    panels = [
        FieldPanel('caption'),
        FieldPanel('caption_en'),
        FieldPanel('link_external'),
        FieldPanel('extra_class'),
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

    youtube_embed_link = models.CharField("Embed для youtube", max_length=255, blank=True)
    youtube_embed_title = models.CharField("Заголовок youtube відео", max_length=255, blank=True)

    branding_link = models.CharField("Посилання для переходу по кліку на брендінг", max_length=255, blank=True)
    branding_slug = models.CharField("Ідентифікатор рекламної кампанії", max_length=255, blank=True)
    branding_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Зображення брендінгу"
    )

    template = "cms_pages/home.jinja"

    class Meta:
        verbose_name = "Головна сторінка"


HomePage.content_panels = [
    FieldPanel('title', classname="full title"),

    # TODO: remove once we'll finally give up with idea of embeded videos
    # FieldPanel('youtube_embed_link', classname="title"),
    # FieldPanel('youtube_embed_title', classname="title"),

    FieldPanel('branding_link', classname="title"),
    FieldPanel('branding_slug', classname="title"),
    ImageChooserPanel('branding_image'),

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

