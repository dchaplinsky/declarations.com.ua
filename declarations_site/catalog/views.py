import math
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import JsonResponse, Http404
from django.conf import settings

from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Search, Q

from cms_pages.models import MetaData, NewsPage, PersonMeta

from .elastic_models import Declaration, NACPDeclaration
from .paginator import paginated_search
from .api import hybrid_response
from .utils import TRANSLITERATOR_SINGLETON, replace_apostrophes
from .models import Office
from .constants import CATALOG_INDICES, OLD_DECLARATION_INDEX


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

        res = search.execute()

        if res.success():
            return list(set(val._source.general.full_name for val in res.suggest.name[0]['options']))
        else:
            return []

    q = replace_apostrophes(request.GET.get('q', '').strip())

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
    if deepsearch:
        fields = ["_all"]
    else:
        fields = [
            "general.last_name",
            "general.name",
            "general.patronymic",
            "general.full_name",
            "general.post.post",
            "general.post.office",
            "general.post.region",
            "intro.declaration_year",
            "intro.doc_type",
            "declaration.source",
            "declaration.url",
        ]

    fmt = request.GET.get("format", "")

    # For now, until we manage how to merge together formats of old and new
    # declarations
    if fmt == "json":
        base_search = Declaration.search()
    else:
        base_search = Search(index=CATALOG_INDICES)

    try:
        meta = PersonMeta.objects.get(fullname=query)
    except PersonMeta.DoesNotExist:
        meta = None

    if query:
        search = base_search.query(
            "multi_match",
            query=query,
            operator="and",
            fields=fields
        )

        if not search.count():
            search = base_search.query(
                "multi_match",
                query=query,
                operator="or",
                minimum_should_match="2",
                fields=fields
            )
    else:
        search = base_search.query('match_all')

    return {
        "query": query,
        "meta": meta,
        "deepsearch": deepsearch,
        "results": paginated_search(request, search)
    }


@hybrid_response('results.jinja')
def fuzzy_search(request):
    query = request.GET.get("q", "")
    search = Declaration.search()
    fuzziness = 1

    if query:
        search = search.query(
            "match", _all={"query": query, "operator": "and"})

        while search.count() == 0 and fuzziness < 3:
            search = Declaration.search().query(
                "match",
                _all={
                    "query": query,
                    "fuzziness": fuzziness,
                    "operator": "and"
                }
            )
            fuzziness += 1
    else:
        search = search.query('match_all')

    return {
        "query": query,
        "fuzziness": fuzziness - 1,
        "results": paginated_search(request, search)
    }


@hybrid_response('declaration.jinja')
def details(request, declaration_id):
    try:
        try:
            declaration = Declaration.get(id=declaration_id)
        except NotFoundError:
            declaration = NACPDeclaration.get(id=declaration_id)
        try:
            meta = PersonMeta.objects.get(
                fullname=declaration.general.full_name,
                year=int(declaration.intro.declaration_year))
        except (PersonMeta.DoesNotExist, ValueError):
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
    search = Search(index=OLD_DECLARATION_INDEX).params(size=0)
    search.aggs.bucket(
        'per_region', 'terms', field='general.post.region.raw', size=30)

    res = search.execute()

    return {
        'facets': res.aggregations.per_region.buckets
    }


@hybrid_response('region_offices.jinja')
def region(request, region_name):
    search = Search(index=OLD_DECLARATION_INDEX)\
        .query(Q('term', general__post__region__raw=region_name) & ~Q('term', general__post__office__raw=''))\
        .params(size=0)

    meta_data = MetaData.objects.filter(
        region_id=region_name,
        office_id=None
    ).first()

    search.aggs.bucket(
        'per_office', 'terms', field='general.post.office.raw', size=1000)
    res = search.execute()

    return {
        'facets': res.aggregations.per_office.buckets,
        'region_name': region_name,
        'title': meta_data.title if meta_data else "",
        'meta_desc': meta_data.description if meta_data else "",
    }


@hybrid_response('results.jinja')
def region_office(request, region_name, office_name):
    # Not using NACP declarations yet to not to blown the list of offices
    search = Search(index=OLD_DECLARATION_INDEX)\
        .query('term', general__post__region__raw=region_name)\
        .query('term', general__post__office__raw=office_name)

    return {
        'query': office_name,
        'results': paginated_search(request, search),
    }


@hybrid_response('results.jinja')
def office(request, office_name):
    search = Search(index=OLD_DECLARATION_INDEX)\
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
