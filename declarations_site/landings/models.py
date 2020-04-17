from itertools import chain

from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.core.serializers.json import DjangoJSONEncoder

from dateutil.parser import parse as dt_parse
from elasticsearch.serializer import JSONSerializer
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
                user_declarant_id=getattr(d.intro, "user_declarant_id", None),
                source=d.api_response(
                    fields=[
                        "guid",
                        "infocard",
                        "raw_source",
                        "unified_source",
                        "related_entities",
                        "guid",
                        "aggregated_data",
                    ]
                ),
            )


class LandingPage(models.Model):
    slug = models.SlugField("Ідентифікатор сторінки", primary_key=True, max_length=100)
    title = models.CharField("Заголовок сторінки", max_length=200)
    description = models.TextField("Опис сторінки", blank=True)
    keywords = models.TextField(
        "Ключові слова для пошуку в деклараціях (по одному запиту на рядок)", blank=True
    )

    def pull_declarations(self):
        for p in self.persons.select_related("body").prefetch_related("declarations"):
            p.pull_declarations()

    def get_summary(self):
        return [
            p.get_summary()
            for p in self.persons.select_related("body").prefetch_related(
                "declarations"
            )
        ]

    def __str__(self):
        return "%s (%s)" % (self.title, self.slug)

    class Meta:
        verbose_name = "Лендінг-сторінка"
        verbose_name_plural = "Лендінг-сторінки"


class Person(models.Model):
    body = models.ForeignKey(
        "LandingPage",
        verbose_name="Лендінг-сторінка",
        related_name="persons",
        on_delete=models.CASCADE,
    )
    name = models.CharField("Ім'я особи", max_length=200)
    extra_keywords = models.CharField(
        "Додаткові ключові слова для пошуку",
        max_length=200,
        blank=True,
        help_text="Ключові слова для додаткового звуження пошуку",
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

        if search_clauses:
            for sc in search_clauses:
                first_pass = (
                    NACPDeclaration.search()
                    .query(
                        "bool",
                        must=[
                            Q(
                                "match",
                                general__full_name={"query": q, "operator": "and"},
                            )
                        ],
                        should=[sc],
                        minimum_should_match=1,
                    )[:100]
                    .execute()
                )

                if first_pass:
                    break
        else:
            first_pass = (
                NACPDeclaration.search()
                .query(
                    "bool",
                    must=[
                        Q("match", general__full_name={"query": q, "operator": "and"})
                    ],
                )[:100]
                .execute()
            )

        Declaration.objects.create_declarations(self, first_pass)

        user_declarant_ids = set(
            filter(
                None,
                self.declarations.exclude(exclude=True).values_list(
                    "user_declarant_id", flat=True
                ),
            )
        )

        if user_declarant_ids:
            second_pass = NACPDeclaration.search().filter(
                "terms", **{"intro.user_declarant_id": list(user_declarant_ids)}
            )

            second_pass = second_pass.execute()

        if not user_declarant_ids or not second_pass:
            obj_ids_to_find = set(
                chain(
                    *self.declarations.exclude(exclude=True).values_list(
                        "obj_ids", flat=True
                    )
                )
            )

            second_pass = NACPDeclaration.search().query(
                "bool",
                must=[
                    Q("match", general__full_name={"query": q, "operator": "or"}),
                    Q("match", obj_ids=" ".join(list(obj_ids_to_find)[:512])),
                ],
                should=[],
                minimum_should_match=0,
            )[:100]

            second_pass = second_pass.execute()

        Declaration.objects.create_declarations(self, second_pass)

    def get_summary(self):
        result = {"name": self.name, "id": self.pk, "documents": []}

        years = {}

        for d in self.declarations.all():
            if d.doc_type == "Форма змін" or d.exclude:
                continue

            if d.year in years:
                if dt_parse(d.source["infocard"]["created_date"]) > dt_parse(
                    years[d.year].source["infocard"]["created_date"]
                ):
                    years[d.year] = d
            else:
                years[d.year] = d

        for k in sorted(years.keys()):
            result["documents"].append(
                {
                    "aggregated_data": years[k].source["aggregated_data"],
                    "year": k,
                    "infocard": years[k].source["infocard"],
                }
            )

        if years:
            result["min_year"] = min(years.keys())
            result["max_year"] = max(years.keys())
        return result

    class Meta:
        verbose_name = "Фокус-персона"
        verbose_name_plural = "Фокус-персони"


class Declaration(models.Model):
    person = models.ForeignKey(
        "Person",
        verbose_name="Персона",
        related_name="declarations",
        on_delete=models.CASCADE,
    )
    declaration_id = models.CharField("Ідентифікатор декларації", max_length=60)
    user_declarant_id = models.IntegerField(
        "Ідентифікатор декларанта", null=True, default=None
    )
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
