import math
import json
from collections import OrderedDict
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import JsonResponse, Http404
from django.conf import settings

from elasticsearch.exceptions import NotFoundError, TransportError
from elasticsearch_dsl import Search, Q

from cms_pages.models import MetaData, NewsPage, PersonMeta

from .elastic_models import Declaration, NACPDeclaration
from .paginator import paginated_search
from .api import hybrid_response
from .utils import TRANSLITERATOR_SINGLETON, replace_apostrophes, base_search_query, apply_search_sorting
from .models import Office
from .constants import CATALOG_INDICES, OLD_DECLARATION_INDEX, NACP_DECLARATION_INDEX


def suggest(request):
    def assume(q, fuzziness):

        search = Search(index=CATALOG_INDICES)\
            .params(size=0)\
            .source(['general.full_name_suggest', 'general.full_name'])\
            .suggest(
                'name',
                q,
                completion={
                    'field': 'general.full_name_suggest',
                    'size': 10,
                    'fuzzy': {
                        'fuzziness': fuzziness,
                        'unicode_aware': True
                    }
                }
        )

        try:
            res = search.execute()

            if res.success() and hasattr(res, 'suggest'):
                return list(set(val._source.general.full_name for val in res.suggest.name[0]['options']))
            else:
                return []
        except TransportError:
            return []

    q = replace_apostrophes(request.GET.get('q', '').strip())
    # Too long request can make elastic sick when applying fuzzy search
    q = q[:40]

    # It seems, that for some reason 'AUTO' setting doesn't work properly
    # for unicode strings
    fuzziness = 0

    if len(q) > 2:
        fuzziness = 1

    suggestions = assume(q, fuzziness)

    if not suggestions:
        suggestions = assume(q, fuzziness + 1)

    return JsonResponse(suggestions, safe=False)


@hybrid_response('results.jinja')
def search(request):
    query = replace_apostrophes(request.GET.get("q", ""))
    deepsearch = bool(request.GET.get("deepsearch", ""))

    fmt = request.GET.get("format", "")

    # For now, until we manage how to merge together formats of old and new
    # declarations
    if fmt == "json":
        base_search = Declaration.search()
    else:
        base_search = Search(index=CATALOG_INDICES).doc_type(
            NACPDeclaration, Declaration
        )


    search = base_search_query(base_search, query, deepsearch, request.GET.copy())
    search = apply_search_sorting(search, request.GET.get("sort", ""))

    try:
        meta = PersonMeta.objects.get(fullname=query)
    except PersonMeta.DoesNotExist:
        meta = None

    return {
        "query": query,
        "meta": meta,
        "deepsearch": deepsearch,
        "results": paginated_search(request, search)
    }


@hybrid_response('results.jinja')
def fuzzy_search(request):
    query = request.GET.get("q", "")
    base_search = Search(
        index=CATALOG_INDICES).doc_type(
        NACPDeclaration, Declaration
    )
    fuzziness = 1

    if query:
        search = base_search.query({
            "match": {
                "general.full_name": {
                    "query": query,
                    "operator": "and"
                }
            }
        })

        while search.count() == 0 and fuzziness < 3:
            search = base_search.query({
                "match": {
                    "general.full_name": {
                        "query": query,
                        "fuzziness": fuzziness,
                        "operator": "and"
                    }
                }
            })
            fuzziness += 1
    else:
        search = base_search.query('match_all')

    return {
        "query": query,
        "fuzziness": fuzziness - 1,
        "results": paginated_search(request, search, 100)
    }


@hybrid_response('declaration.jinja')
def details(request, declaration_id):
    try:
        try:
            declaration = NACPDeclaration.get(id=declaration_id)
        except NotFoundError:
            declaration = Declaration.get(id=declaration_id)
        try:
            meta = PersonMeta.objects.get(
                fullname=declaration.general.full_name,
                year=int(declaration.intro.declaration_year))
        except (PersonMeta.DoesNotExist, ValueError, TypeError):
            try:
                meta = PersonMeta.objects.get(
                    fullname=declaration.general.full_name,
                    year__isnull=True)
            except PersonMeta.DoesNotExist:
                meta = None

        if "source" in request.GET:
            return redirect(
                declaration["declaration"]["url"] or
                reverse("details", kwargs={"declaration_id": declaration._id})
            )

    except (ValueError, NotFoundError):
        raise Http404("Таких не знаємо!")

    return {
        "declaration": declaration,
        "transliterations": TRANSLITERATOR_SINGLETON.transliterate(
            getattr(declaration.general, "last_name", ""),
            getattr(declaration.general, "name", ""),
            getattr(declaration.general, "patronymic", ""),
        ),
        "meta": meta
    }


@hybrid_response('regions.jinja')
def regions_home(request):
    search = Search(index=CATALOG_INDICES).params(size=0)
    search.aggs.bucket(
        'per_region', 'terms', field='general.post.region.raw', size=30)

    res = search.execute()

    return {
        'facets': res.aggregations.per_region.buckets
    }


@hybrid_response('region_offices.jinja')
def region(request, region_name):
    search = Search(index=CATALOG_INDICES)\
        .query(Q('term', general__post__region__raw=region_name) & ~Q('term', general__post__office__raw=''))\
        .params(size=0)

    meta_data = MetaData.objects.filter(
        region_id=region_name,
        office_id=None
    ).first()

    search.aggs.bucket(
        'per_office', 'terms', field='general.post.office.raw', size=100)
    res = search.execute()

    return {
        'facets': res.aggregations.per_office.buckets,
        'region_name': region_name,
        'title': meta_data.title if meta_data else "",
        'meta_desc': meta_data.description if meta_data else "",
    }


@hybrid_response('results.jinja')
def region_office(request, region_name, office_name):
    search = Search(index=CATALOG_INDICES)\
        .doc_type(NACPDeclaration, Declaration)\
        .query('term', general__post__region__raw=region_name)\
        .query('term', general__post__office__raw=office_name)

    return {
        'query': office_name,
        'results': paginated_search(request, search),
    }


@hybrid_response('results.jinja')
def office(request, office_name):
    search = Search(index=CATALOG_INDICES)\
        .doc_type(NACPDeclaration, Declaration)\
        .query('term', general__post__office__raw=office_name)

    return {
        'query': office_name,
        'results': paginated_search(request, search)
    }


def sitemap_general(request):
    # TODO: REFACTOR ME?
    urls = [
        reverse("wagtail_serve", args=[""]),
        reverse("wagtail_serve", args=["about/"]),
        reverse("wagtail_serve", args=["api/"]),
        reverse("wagtail_serve", args=["news/"]),
        reverse("regions_home"),
        reverse("business_intelligence"),
    ]

    for news in NewsPage.objects.live():
        urls.append(news.url)

    search = Search(index=OLD_DECLARATION_INDEX).params(size=0)
    search.aggs.bucket(
        'per_region', 'terms', field='general.post.region.raw', size=30)

    for r in search.execute().aggregations.per_region.buckets:
        if r.key == "":
            continue

        urls.append(reverse("region", kwargs={"region_name": r.key}))

        subsearch = Search(index=OLD_DECLARATION_INDEX)\
            .query(Q('term', general__post__region__raw=r.key) & ~Q('term', general__post__office_raw=''))\
            .params(size=0)

        subsearch.aggs.bucket(
            'per_office', 'terms', field='general.post.office.raw', size=1000)

        for subr in subsearch.execute().aggregations.per_office.buckets:
            if subr.key == '':
                continue
            urls.append(reverse(
                "region_office",
                kwargs={"region_name": r.key, "office_name": subr.key}))

    search = Search(index=OLD_DECLARATION_INDEX).params(size=0)
    search.aggs.bucket(
        'per_office', 'terms', field='general.post.office.raw', size=5000)

    for r in search.execute().aggregations.per_office.buckets:
        if r.key == "":
            continue

        urls.append(reverse("office", kwargs={"office_name": r.key}))

    return render(request, "sitemap.jinja",
                  {"urls": urls}, content_type="application/xml")


def sitemap_declarations(request, page):
    page = int(page)
    urls = []

    search = Search(index=CATALOG_INDICES).extra(stored_fields=[])
    search = search[(page - 1) * settings.SITEMAP_DECLARATIONS_PER_PAGE:page * settings.SITEMAP_DECLARATIONS_PER_PAGE]

    for r in search.execute():
        urls.append(reverse("details", kwargs={"declaration_id": r.meta.id}))

    return render(request, "sitemap.jinja",
                  {"urls": urls}, content_type="application/xml")


def sitemap_index(request):
    urls = [
        reverse("sitemap_general"),
    ]

    decl_count = Search(index=CATALOG_INDICES).extra(stored_fields=[]).count()

    pages = math.ceil(decl_count / settings.SITEMAP_DECLARATIONS_PER_PAGE)
    for i in range(pages):
        urls.append(reverse("sitemap_declarations", kwargs={"page": i + 1}))

    return render(request, "sitemap_index.jinja",
                  {"urls": urls}, content_type="application/xml")


def offices_home(request):
    return render(request, "offices.jinja",
                  {"offices": Office.dump_bulk()})


def business_intelligence(request):
    return render(request, "bi.jinja")


def business_intelligence_alt(request):
    return render(request, "bi_alt.jinja")


def prepare_datasets_for_charts(declarations, labels, columns):
    colors = [
        "rgba(54, 162, 235, 1)",
        "rgba(255, 99, 132, 1)",
        "rgba(255, 206, 86, 1)",
        "rgba(206, 255, 86, 1)",
    ]

    results = {
        "labels": labels,
        "datasets": []
    }

    results_breakdown = OrderedDict((
        (col_key, [])) for col_key in columns.keys()
    )

    for r in declarations:
        for col_key, col_settings in columns.items():
            results_breakdown[col_key].append(
                col_settings["transform"](r.aggregated[col_settings["field"]])
            )

    for i, (label, data) in enumerate(results_breakdown.items()):
        data = {
            "label": label,
            "backgroundColor": colors[i],
            "data": data,
            "type": columns[label]["type"]
        }

        if columns[label]["type"] == "line":
            data.update({
                "type": "line",
                "lineTension": 0,
                "backgroundColor": None
            })

        results["datasets"].append(
            data
        )

    return results


@hybrid_response('compare.jinja')
def compare_declarations(request):
    declarations = [
        decl_id
        for decl_id in request.GET.getlist("declaration_id", [])
        if decl_id
    ][:10]

    if not declarations:
        return {}

    search = Search(
        index=CATALOG_INDICES).doc_type(NACPDeclaration, Declaration) \
        .query(
            {
                "ids": {
                    "values": declarations
                }
            })
    results = search.execute()

    results = sorted(results, key=lambda x: str(
        x.intro.date or x.declaration.date or x.intro.declaration_year or "")
    )

    results = [r for r in results if hasattr(r, "aggregated")]

    add_names_to_labels = len(set(r.general.full_name.lower() for r in results)) > 1
    add_types_to_labels = len(set((getattr(r.intro, "doc_type", "щорічна")).lower() for r in results)) > 1
    labels = []
    urls = []
    for r in results:
        label = str(r.intro.declaration_year)
        if add_types_to_labels:
            label += ", " + getattr(r.intro, "doc_type", "щорічна")

        if getattr(r.intro, "corrected", False):
            label += ", уточнена"

        if add_names_to_labels:
            label += ", " + r.general.full_name

        labels.append(label)
        urls.append(reverse("details", kwargs={"declaration_id": r._id}))

    # TODO: move to a separate file
    return {
        "results": results,
        "labels": labels,
        "urls": json.dumps(urls),
        "incomes_data": json.dumps(prepare_datasets_for_charts(
            results, labels,
            OrderedDict((
                ("Загальна сума подарунків", {"type": "line", "field": "incomes.presents.all", "transform": float}),
                ("Родина", {"type": "bar", "field": "incomes.family", "transform": float}),
                ("Декларант", {"type": "bar", "field": "incomes.declarant", "transform": float}),
            )))
        ),

        "assets_data": json.dumps(prepare_datasets_for_charts(
            results, labels,
            OrderedDict((
                ("Загальна сума готівки", {"type": "line", "field": "assets.cash.total", "transform": float}),
                ("Родина", {"type": "bar", "field": "assets.family", "transform": float}),
                ("Декларант", {"type": "bar", "field": "assets.declarant", "transform": float}),
            )))
        ),

        "incomes_vs_expenses_data": json.dumps(prepare_datasets_for_charts(
            results, labels,
            OrderedDict((
                ("Дохід", {"type": "bar", "field": "incomes.total", "transform": float}),
                ("Грошові активи", {"type": "bar", "field": "assets.total", "transform": float}),
                ("Фінансові зобов'язання",
                    {"type": "bar", "field": "liabilities.total", "transform": lambda x: -float(x)}
                 ),
                ("Витрати",
                    {"type": "bar", "field": "expenses.total", "transform": lambda x: -float(x)}
                 ),
            )))
        ),

        "incomes_vs_expenses_data": json.dumps(prepare_datasets_for_charts(
            results, labels,
            OrderedDict((
                ("Дохід", {"type": "bar", "field": "incomes.total", "transform": float}),
                ("Грошові активи", {"type": "bar", "field": "assets.total", "transform": float}),
                ("Фінансові зобов'язання",
                    {"type": "bar", "field": "liabilities.total", "transform": lambda x: -float(x)}
                 ),
                ("Витрати",
                    {"type": "bar", "field": "expenses.total", "transform": lambda x: -float(x)}
                 ),
            )))
        ),

        "land_data": json.dumps(prepare_datasets_for_charts(
            results, labels,
            OrderedDict((
                ("Площа в родини", {"type": "bar", "field": "estate.family_land", "transform": float}),
                ("Площа в декларанта", {"type": "bar", "field": "estate.declarant_land", "transform": float}),
            )))
        ),

        "realty_data": json.dumps(prepare_datasets_for_charts(
            results, labels,
            OrderedDict((
                ("Площа в родини", {"type": "bar", "field": "estate.family_other", "transform": float}),
                ("Площа в декларанта", {"type": "bar", "field": "estate.declarant_other", "transform": float}),
            )))
        ),

        "cars_data": json.dumps(prepare_datasets_for_charts(
            results, labels,
            OrderedDict((
                ("Кількість у декларації", {"type": "bar", "field": "vehicles.all_names",
                 "transform": lambda x: len(x.split(";")) if x else 0}),
            )))
        ),
    }
