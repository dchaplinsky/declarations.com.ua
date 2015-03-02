from catalog.elastic_models import Declaration


def stats_processor(request):
    s = Declaration.search()
    res = s.params(search_type="count").aggs.metric(
        "distinct_names", "cardinality",
        script=("doc['general.name'].value + ' ' + "
                "doc['general.patronymic'].value + ' ' + "
                "doc['general.last_name'].value")).execute()

    return {
        'total_declarations': s.count(),
        'total_persons': res.aggregations.distinct_names.value
    }
