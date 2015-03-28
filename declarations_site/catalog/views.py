from django.shortcuts import render
from django.http import JsonResponse, Http404
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl.filter import Term, Not

from catalog.elastic_models import Declaration


def home(request):
    return render(request, "home.jinja", {})


def suggest(request):
    search = Declaration.search()\
        .suggest(
            'name',
            request.GET.get('q', ''),
            completion={
                'field': 'general.full_name_suggest',
                'size': 10,
                'fuzzy': {
                    'fuzziness': 3,
                    'unicode_aware': 1
                }
            }
        )
    res = search.execute()

    if res.success():
        return JsonResponse(
            [val['text'] for val in res.suggest['name'][0]['options']],
            safe=False
        )
    else:
        return JsonResponse([], safe=False)


def search(request):
    query = request.GET.get("q", "")
    results = Declaration.search().query(
        "match", _all=query)[:30]

    return render(request, "results.jinja", {
        "query": query,
        "results": results.execute()
    })


def details(request, declaration_id):
    try:
        declaration = Declaration.get(id=int(declaration_id))
    except (ValueError, NotFoundError):
        raise Http404("Таких не знаємо!")

    return render(request, "declaration.jinja", {
        "declaration": declaration
    })


def regions_home(request):
    search = Declaration.search().params(search_type="count")
    search.aggs.bucket(
        'per_region', 'terms', field='general.post.region')
    res = search.execute()

    return render(request, 'regions.jinja', {
        'facets': res.aggregations.per_region.buckets
    })


def region(request, region_name):
    search = Declaration.search()\
        .filter(
            Term(general__post__region=region_name) &
            Not(Term(general__post__office='')))\
        .params(search_type="count")

    search.aggs.bucket(
        'per_office', 'terms', field='general.post.office')
    res = search.execute()

    return render(request, 'region_offices.jinja', {
        'facets': res.aggregations.per_office.buckets,
        'region_name': region_name
    })


def region_office(request, region_name, office_name):
    search = Declaration.search()\
        .filter('term', general__post__region=region_name)\
        .filter('term', general__post__office=office_name)

    return render(request, 'results.jinja', {
        'query': office_name,
        'results': search.execute()
    })


def office(request, office_name):
    search = Declaration.search()\
        .filter('term', general__post__office=office_name)[:30]

    return render(request, 'results.jinja', {
        'query': office_name,
        'results': search.execute()
    })
