from django.shortcuts import render
from django.http import JsonResponse, Http404
from elasticsearch.exceptions import NotFoundError

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
        return JsonResponse([val['text'] for val in res.suggest['name'][0]['options']], safe=False)
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
