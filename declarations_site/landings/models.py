from itertools import chain

from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from elasticsearch.serializer import JSONSerializer
from django.core.serializers.json import DjangoJSONEncoder

from elasticsearch_dsl import Q

from catalog.elastic_models import NACPDeclaration


class DeclarationsManager(models.Manager):
    def create_declarations(self, person, declarations):
        existing_ids = self.filter(person=person).values_list(
            "declaration_id", flat=True
        )

        for d in declarations:
            if d._id in existing_ids:
                continue

            self.create(
                person=person,
                declaration_id=d._id,
                year=d.intro.declaration_year,
                corrected=getattr(d.intro, "corrected", False),
                doc_type=getattr(d.intro, "doc_type", "Щорічна"),
                obj_ids=list(getattr(d, "obj_ids", [])),
                source= d.api_response(
                    fields=[
                        "guid",
                        "infocard",
                        "raw_source",
                        "unified_source",
                        "related_entities",
                        "guid",
                        "aggregated_data",
                        "related_documents",
                    ]
                ),
            )


class LandingPage(models.Model):
    slug = models.SlugField("Ідентифікатор сторінки", primary_key=True, max_length=100)
    title = models.CharField("Заголовок сторінки", max_length=200)
    description = models.TextField("Опис сторінки", blank=True)
    keywords = models.TextField(
        "Ключові слова для пошуку в деклараціях (по одному запиту на рядок)"
    )

    def pull_declarations(self):
        for p in self.persons.select_related("body").prefetch_related("declarations"):
            p.pull_declarations()

    def __str__(self):
        return "%s (%s)" % (self.title, self.slug)

    class Meta:
        verbose_name = "Лендінг-сторінка"
        verbose_name_plural = "Лендінг-сторінки"


class Person(models.Model):
    body = models.ForeignKey(
        "LandingPage", verbose_name="Лендінг-сторінка", related_name="persons"
    )
    name = models.CharField("Ім'я особи", max_length=200)
    extra_keywords = models.CharField(
        "Додаткові ключові слова для пошуку", max_length=200, blank=True,
        help_text="Ключові слова для додаткового звуження пошуку"
    )

    def __str__(self):
        return "%s (знайдено декларацій: %s)" % (self.name, self.declarations.count())

    def pull_declarations(self):
        def get_search_clause(kwd):
            if "область" not in kwd:
                return Q(
                    "multi_match",
                    query=kwd,
                    operator="or",
                    minimum_should_match=1,
                    fields=[
                        "general.post.region",
                        "general.post.office",
                        "general.post.post",
                        "general.post.actual_region",
                    ],
                )
            else:
                return Q(
                    "multi_match",
                    query=kwd,
                    fields=["general.post.region", "general.post.actual_region"],
                )

        search_clauses = [
            get_search_clause(x)
            for x in filter(None, map(str.strip, self.body.keywords.split("\n")))
        ]

        q = "{} {}".format(self.name, self.extra_keywords)

        for sc in search_clauses:
            first_pass = (
                NACPDeclaration.search()
                .query(
                    "bool",
                    must=[Q("match", general__full_name={"query": q, "operator": "and"})],
                    should=[sc],
                    minimum_should_match=1,
                )[:100]
                .execute()
            )

            if first_pass:
                break

        Declaration.objects.create_declarations(self, first_pass)
        obj_ids_to_find = set(
            chain(*self.declarations.exclude(exclude=True).values_list("obj_ids", flat=True))
        )

        second_pass = (
            NACPDeclaration.search()
            .query(
                "bool",
                must=[
                    Q("match", general__full_name={"query": q, "operator": "or"}),
                    Q("match", obj_ids=" ".join(obj_ids_to_find)),
                ],
                should=[],
                minimum_should_match=0,
            )[:100]
        )

        second_pass = second_pass.execute()

        Declaration.objects.create_declarations(self, second_pass)

    class Meta:
        verbose_name = "Фокус-персона"
        verbose_name_plural = "Фокус-персони"


class Declaration(models.Model):
    person = models.ForeignKey(
        "Person", verbose_name="Персона", related_name="declarations"
    )
    declaration_id = models.CharField("Ідентифікатор декларації", max_length=60)
    year = models.IntegerField("Рік подання декларації")
    corrected = models.BooleanField("Уточнена декларація")
    exclude = models.BooleanField("Ігнорувати цей документ", default=False)
    doc_type = models.CharField("Тип документу", max_length=50)
    source = JSONField("Машиночитний вміст", default=dict, encoder=DjangoJSONEncoder)
    obj_ids = ArrayField(
        models.CharField(max_length=50),
        verbose_name="Ідентифікатори з декларації",
        default=list,
    )

    objects = DeclarationsManager()

    class Meta:
        verbose_name = "Декларація фокус-персони"
        verbose_name_plural = "Декларація фокус-персони"

        index_together = [["year", "corrected", "doc_type", "exclude"]]

        unique_together = [["person", "declaration_id"]]
        ordering = ["-year", "-corrected"]
