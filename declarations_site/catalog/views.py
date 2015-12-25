from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import JsonResponse, Http404

from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl.filter import Term, Not

from catalog.elastic_models import Declaration
from catalog.paginator import paginated_search
from catalog.api import hybrid_response
from catalog.models import Office
from cms_pages.models import MetaData, NewsPage


def suggest(request):
    def assume(q, fuzziness):
        search = Declaration.search()\
            .suggest(
                'name',
                q,
                completion={
                    'field': 'general.full_name_suggest',
                    'size': 10,
                    'fuzzy': {
                        'fuzziness': fuzziness,
                        'unicode_aware': 1
                    }
                }
        )

        res = search.execute()

        if res.success():
            return [val['text'] for val in res.suggest['name'][0]['options']]
        else:
            []

    q = request.GET.get('q', '').strip()

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
    query = request.GET.get("q", "")
    search = Declaration.search()
    if query:
        search = search.query(
            "match", _all={"query": query, "operator": "and"})

        if not search.count():
            search = Declaration.search().query(
                "match",
                _all={
                    "query": query,
                    "operator": "or",
                    "minimum_should_match": "2"
                }
            )
    else:
        search = search.query('match_all')

    return {
        "query": query,
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
        declaration = Declaration.get(id=declaration_id)
    except (ValueError, NotFoundError):
        raise Http404("Таких не знаємо!")

    return {
        "declaration": declaration
    }


@hybrid_response('regions.jinja')
def regions_home(request):
    search = Declaration.search().params(search_type="count")
    search.aggs.bucket(
        'per_region', 'terms', field='general.post.region', size=0)

    res = search.execute()

    return {
        'facets': res.aggregations.per_region.buckets
    }


@hybrid_response('region_offices.jinja')
def region(request, region_name):
    search = Declaration.search()\
        .filter(
            Term(general__post__region=region_name) &
            Not(Term(general__post__office='')))\
        .params(search_type="count")

    meta_data = MetaData.objects.filter(
        region_id=region_name,
        office_id=None
    ).first()

    search.aggs.bucket(
        'per_office', 'terms', field='general.post.office', size=0)
    res = search.execute()

    return {
        'facets': res.aggregations.per_office.buckets,
        'region_name': region_name,
        'title': meta_data.title if meta_data else "",
        'meta_desc': meta_data.description if meta_data else "",
    }


@hybrid_response('results.jinja')
def region_office(request, region_name, office_name):
    search = Declaration.search()\
        .filter('term', general__post__region=region_name)\
        .filter('term', general__post__office=office_name)

    return {
        'query': office_name,
        'results': paginated_search(request, search),
    }


@hybrid_response('results.jinja')
def office(request, office_name):
    search = Declaration.search()\
        .filter('term', general__post__office=office_name)

    return {
        'query': office_name,
        'results': paginated_search(request, search)
    }


def sitemap(request):
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

    search = Declaration.search().params(search_type="count")
    search.aggs.bucket(
        'per_region', 'terms', field='general.post.region', size=0)

    for r in search.execute().aggregations.per_region.buckets:
        if r.key == "":
            continue

        urls.append(reverse("region", kwargs={"region_name": r.key}))

        subsearch = Declaration.search()\
            .filter(
                Term(general__post__region=r.key) &
                Not(Term(general__post__office='')))\
            .params(search_type="count")

        subsearch.aggs.bucket(
            'per_office', 'terms', field='general.post.office', size=0)

        for subr in subsearch.execute().aggregations.per_office.buckets:
            urls.append(reverse(
                "region_office",
                kwargs={"region_name": r.key, "office_name": subr.key}))

    search = Declaration.search().params(search_type="count")
    search.aggs.bucket(
        'per_office', 'terms', field='general.post.office', size=0)

    for r in search.execute().aggregations.per_office.buckets:
        if r.key == "":
            continue

        urls.append(reverse("office", kwargs={"office_name": r.key}))

    search = Declaration.search().extra(fields=[], size=100000)
    for r in search.execute():
        urls.append(reverse("details", kwargs={"declaration_id": r._id}))

    return render(request, "sitemap.jinja",
                  {"urls": urls}, content_type="application/xml")


def offices_home(request):
    return render(request, "offices.jinja",
                  {"offices": Office.dump_bulk()})


def business_intelligence(request):
    return render(request, "bi.jinja")
