from django.shortcuts import render
from django.http import JsonResponse
from elasticsearch_dsl.connections import connections


def home(request):
    return render(request, "home.jinja", {})


def suggest(request):
    client = connections.get_connection()

    res = client.suggest(index="catalog", body={
        "declarations": {
            "text": request.GET.get("q", ""),
            "completion": {
                "field": "general.full_name_suggest",
                "size": 10,
                "fuzzy": {
                    "fuzziness": 3,
                    "unicode_aware": 1
                }
            }
        }}
    )

    try:
        options = res["declarations"][0]["options"]

        return JsonResponse([val["text"] for val in options], safe=False)
    except (IndexError, KeyError):
        return JsonResponse([], safe=False)
