import math
import json
from collections import OrderedDict
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse, Http404
from django.conf import settings
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.utils.translation import gettext as _, get_language

from django.views import View
from django.template.loader import render_to_string

from elasticsearch.exceptions import NotFoundError, TransportError
from elasticsearch_dsl import Search, Q

from cms_pages.models import MetaData, NewsPage, PersonMeta
from dateutil.parser import parse as dt_parse

from .elastic_models import Declaration, NACPDeclaration, NACPDeclarationNewFormat
from .paginator import paginated_search
from .api import hybrid_response
from .utils import replace_apostrophes, base_search_query, apply_search_sorting, orig_translate_url, robust_getlist
from .models import Office
from .translator import Translator, NoOpTranslator
from .constants import CATALOG_INDICES, OLD_DECLARATION_INDEX, NACP_DECLARATION_NEW_FORMAT_INDEX


class SuggestView(View):
    def get(self, request):
        q = request.GET.get("q", "").strip()

        suggestions = []
        seen = set()

        s = (
            Search(index=CATALOG_INDICES)
            .source(["names_autocomplete"])
            .highlight("names_autocomplete")
            .highlight_options(
                order="score",
                fragment_size=100,
                number_of_fragments=10,
                pre_tags=["<strong>"],
                post_tags=["</strong>"],
            )
        )

        s = s.query(
            "bool",
            must=[Q("match", names_autocomplete={"query": q, "operator": "and"})],
            should=[
                Q("match_phrase", names_autocomplete__raw={"query": q, "boost": 2}),
                Q(
                    "match_phrase_prefix",
                    names_autocomplete__raw={"query": q, "boost": 2},
                ),
            ],
        )[:10]

        res = s.execute()

        for r in res:
            if "names_autocomplete" in r.meta.highlight:
                for candidate in r.meta.highlight["names_autocomplete"]:
                    if candidate.lower() not in seen:
                        suggestions.append(candidate)
                        seen.add(candidate.lower())

        # Add number of sources where it was found

        rendered_result = [
            render_to_string("autocomplete.jinja", {"result": {"hl": k}})
            for k in suggestions[:20]
        ]

        return JsonResponse(rendered_result, safe=False)


@hybrid_response('results.jinja')
def search(request):
    language = get_language()

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

    try:
        results = paginated_search(request, search)
    except EmptyPage:
        raise Http404("Page is empty")
    except PageNotAnInteger:
        raise Http404("No page")

    for r in results:
        r.prepare_translations(language, infocard_only=True)

    return {
        "query": query,
        "meta": meta,
        "deepsearch": deepsearch,
        "results": results,
        "language": language,
    }


@hybrid_response('results.jinja')
def fuzzy_search(request):
    number_of_results = {
        1: 300,
        2: 100,
        3: 100
    }
    query = request.GET.get("q", "")
    submitted_since = replace_apostrophes(request.GET.get("submitted_since", ""))
    user_declarant_ids = set(filter(str.isdigit, robust_getlist(request.GET, "user_declarant_ids")))

    base_search = Search(
        index=CATALOG_INDICES + (NACP_DECLARATION_NEW_FORMAT_INDEX, )).doc_type(
        NACPDeclarationNewFormat, NACPDeclaration, Declaration
    )

    if submitted_since:
        base_search = base_search.query(
            "range",
            intro__date={
                "gte": dt_parse(submitted_since, dayfirst=True)
            }
        )

    if user_declarant_ids:
        base_search = base_search.query("terms", intro__user_declarant_id=list(user_declarant_ids))

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
        "results": paginated_search(request, search, number_of_results.get(fuzziness, 100))
    }


@hybrid_response("declaration.jinja")
def details(request, declaration_id):
    language = get_language()
    try:
        try:
            declaration = NACPDeclaration.get(id=declaration_id)
        except NotFoundError:
            declaration = Declaration.get(id=declaration_id)

        declaration.prepare_translations(language)

        try:
            meta = PersonMeta.objects.get(
                fullname=declaration.general.full_name,
                year=int(declaration.intro.declaration_year),
            )
        except (PersonMeta.DoesNotExist, ValueError, TypeError):
            try:
                meta = PersonMeta.objects.get(
                    fullname=declaration.general.full_name, year__isnull=True
                )
            except PersonMeta.DoesNotExist:
                meta = None

        if "source" in request.GET:
            return redirect(
                declaration.original_url
                or reverse("details", kwargs={"declaration_id": declaration._id})
            )

    except (ValueError, NotFoundError):
        if "source" in request.GET:
            return redirect(
                # Temporary hack to enable redirect for new declarations that are yet not in main
                # index
                "http://public.nazk.gov.ua/documents/" + declaration_id.replace("nacp_", "")
            )

        raise Http404("Таких не знаємо!")

    return {"declaration": declaration, "language": language, "meta": meta}


@hybrid_response("regions.jinja")
def regions_home(request):
    language = get_language()
    search = Search(index=CATALOG_INDICES).params(size=0)
    search.aggs.bucket("per_region", "terms", field="general.post.region.raw", size=30)

    res = search.execute()

    if language == "en":
        translator = Translator()
        to_translate = []

        for f in res.aggregations.per_region.buckets:
            to_translate.append(f.key)

        translator.fetch_partial_dict_from_db(to_translate)
    else:
        translator = NoOpTranslator()

    return {
        "facets": res.aggregations.per_region.buckets,
        "language": language,
        "translator": translator,
    }


@hybrid_response("region_offices.jinja")
def region(request, region_name):
    language = get_language()

    search = (
        Search(index=CATALOG_INDICES)
        .query(
            Q("term", general__post__region__raw=region_name)
            & ~Q("term", general__post__office__raw="")
        )
        .params(size=0)
    )

    meta_data = MetaData.objects.filter(region_id=region_name, office_id=None).first()

    search.aggs.bucket("per_office", "terms", field="general.post.office.raw", size=100)
    res = search.execute()

    if language == "en":
        translator = Translator()
        to_translate = [region_name]

        for f in res.aggregations.per_office.buckets:
            to_translate.append(f.key)

        translator.fetch_partial_dict_from_db(to_translate)
    else:
        translator = NoOpTranslator()

    return {
        "language": language,
        "translator": translator,
        "facets": res.aggregations.per_office.buckets,
        "region_name": region_name,
        "title": meta_data.title if meta_data else "",
        "meta_desc": meta_data.description if meta_data else "",
    }


@hybrid_response("results.jinja")
def region_office(request, region_name, office_name):
    language = get_language()

    search = (
        Search(index=CATALOG_INDICES)
        .doc_type(NACPDeclaration, Declaration)
        .query("term", general__post__region__raw=region_name)
        .query("term", general__post__office__raw=office_name)
    )

    results = paginated_search(request, search)

    if language == "en":
        translator = Translator()
        to_translate = [region_name, office_name]

        translator.fetch_partial_dict_from_db(to_translate)
    else:
        translator = NoOpTranslator()

    for r in results:
        r.prepare_translations(language, infocard_only=True)

    return {
        "language": language,
        "exact_query": translator.translate(office_name)["translation"],
        "deepsearch": True,
        "results": results,
        "translator": translator,
    }


@hybrid_response("results.jinja")
def office(request, office_name):
    language = get_language()

    search = (
        Search(index=CATALOG_INDICES)
        .doc_type(NACPDeclaration, Declaration)
        .query("term", general__post__office__raw=office_name)
    )

    results = paginated_search(request, search)

    if language == "en":
        translator = Translator()
        to_translate = [office_name]

        translator.fetch_partial_dict_from_db(to_translate)
    else:
        translator = NoOpTranslator()

    for r in results:
        r.prepare_translations(language, infocard_only=True)

    return {
        "language": language,
        "exact_query": translator.translate(office_name)["translation"],
        "results": results,
        "deepsearch": True,
        "translator": translator,
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
            "borderWidth": 0,
            "data": data,
            "order": i,
            "type": columns[label]["type"]
        }

        if columns[label]["type"] == "line":
            data.update({
                "type": "line",
                "lineTension": 0,
                "backgroundColor": "rgba(0, 0, 0, 0.2)",
            })

        results["datasets"].append(
            data
        )

    return results


@hybrid_response("compare.jinja")
def compare_declarations(request):
    language = get_language()

    declarations = robust_getlist(request.GET, "declaration_id")

    declarations = [
        decl_id for decl_id in set(declarations) if decl_id
    ][:10]

    if not declarations:
        return {}

    search = (
        Search(index=CATALOG_INDICES)
        .doc_type(NACPDeclaration, Declaration)
        .query({"ids": {"values": declarations}})
    )
    results = search.execute()

    results = sorted(
        results,
        key=lambda x: (
            str(x.intro.declaration_year or x.intro.date or x.declaration.date or ""),
            getattr(x.intro, "corrected", False),
            getattr(x, "source", "").lower() not in ["vulyk", "chesno"]
        ),
    )

    results = [r for r in results if hasattr(r, "aggregated")]
    for r in results:
        r.prepare_translations(language, infocard_only=True)

    add_names_to_labels = len(set(r.general.full_name.lower() for r in results)) > 1
    add_types_to_labels = (
        len(
            set(
                (getattr(r.intro, "doc_type", "щорічна") or "щорічна").lower()
                for r in results
            )
        )
        > 1
    )
    labels = []
    urls = []
    for r in results:
        label = str(r.intro.declaration_year)
        if add_types_to_labels:
            label += ", " + _(getattr(r.intro, "doc_type", "щорічна") or "щорічна")

        if getattr(r.intro, "corrected", False):
            label += ", " + _("уточнена")

        if add_names_to_labels:
            label += ", " + r._full_name(language)

        labels.append(label)
        urls.append(reverse("details", kwargs={"declaration_id": r._id}))

    # TODO: move to a separate file
    return {
        "language": language,
        "results": results,
        "labels": labels,
        "urls": json.dumps(urls),
        "incomes_data": json.dumps(
            prepare_datasets_for_charts(
                results,
                labels,
                OrderedDict(
                    (
                        (
                            _("Загальна сума подарунків"),
                            {
                                "type": "line",
                                "field": "incomes.presents.all",
                                "transform": float,
                            },
                        ),
                        (
                            _("Родина"),
                            {
                                "type": "bar",
                                "field": "incomes.family",
                                "transform": float,
                            },
                        ),
                        (
                            _("Декларант"),
                            {
                                "type": "bar",
                                "field": "incomes.declarant",
                                "transform": float,
                            },
                        ),
                    )
                ),
            )
        ),
        "assets_data": json.dumps(
            prepare_datasets_for_charts(
                results,
                labels,
                OrderedDict(
                    (
                        (
                            _("Загальна сума готівки"),
                            {
                                "type": "line",
                                "field": "assets.cash.total",
                                "transform": float,
                            },
                        ),
                        (
                            _("Родина"),
                            {
                                "type": "bar",
                                "field": "assets.family",
                                "transform": float,
                            },
                        ),
                        (
                            _("Декларант"),
                            {
                                "type": "bar",
                                "field": "assets.declarant",
                                "transform": float,
                            },
                        ),
                    )
                ),
            )
        ),
        "incomes_vs_expenses_data": json.dumps(
            prepare_datasets_for_charts(
                results,
                labels,
                OrderedDict(
                    (
                        (
                            _("Дохід"),
                            {
                                "type": "bar",
                                "field": "incomes.total",
                                "transform": float,
                            },
                        ),
                        (
                            _("Грошові активи"),
                            {
                                "type": "bar",
                                "field": "assets.total",
                                "transform": float,
                            },
                        ),
                        (
                            _("Фінансові зобов'язання"),
                            {
                                "type": "bar",
                                "field": "liabilities.total",
                                "transform": lambda x: -float(x),
                            },
                        ),
                        (
                            _("Витрати"),
                            {
                                "type": "bar",
                                "field": "expenses.total",
                                "transform": lambda x: -float(x),
                            },
                        ),
                    )
                ),
            )
        ),
        "incomes_vs_expenses_data": json.dumps(
            prepare_datasets_for_charts(
                results,
                labels,
                OrderedDict(
                    (
                        (
                            _("Дохід"),
                            {
                                "type": "bar",
                                "field": "incomes.total",
                                "transform": float,
                            },
                        ),
                        (
                            _("Грошові активи"),
                            {
                                "type": "bar",
                                "field": "assets.total",
                                "transform": float,
                            },
                        ),
                        (
                            _("Фінансові зобов'язання"),
                            {
                                "type": "bar",
                                "field": "liabilities.total",
                                "transform": lambda x: -float(x),
                            },
                        ),
                        (
                            _("Витрати"),
                            {
                                "type": "bar",
                                "field": "expenses.total",
                                "transform": lambda x: -float(x),
                            },
                        ),
                    )
                ),
            )
        ),
        "land_data": json.dumps(
            prepare_datasets_for_charts(
                results,
                labels,
                OrderedDict(
                    (
                        (
                            _("Площа в родини"),
                            {
                                "type": "bar",
                                "field": "estate.family_land",
                                "transform": float,
                            },
                        ),
                        (
                            _("Площа в декларанта"),
                            {
                                "type": "bar",
                                "field": "estate.declarant_land",
                                "transform": float,
                            },
                        ),
                    )
                ),
            )
        ),
        "realty_data": json.dumps(
            prepare_datasets_for_charts(
                results,
                labels,
                OrderedDict(
                    (
                        (
                            _("Площа в родини"),
                            {
                                "type": "bar",
                                "field": "estate.family_other",
                                "transform": float,
                            },
                        ),
                        (
                            _("Площа в декларанта"),
                            {
                                "type": "bar",
                                "field": "estate.declarant_other",
                                "transform": float,
                            },
                        ),
                    )
                ),
            )
        ),
        "cars_data": json.dumps(
            prepare_datasets_for_charts(
                results,
                labels,
                OrderedDict(
                    (
                        (
                            _("Кількість у декларації"),
                            {
                                "type": "bar",
                                "field": "vehicles.all_names",
                                "transform": lambda x: len(x.split(";")) if x else 0,
                            },
                        ),
                    )
                ),
            )
        ),
    }
