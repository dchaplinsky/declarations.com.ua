from catalog.elastic_models import Declaration


def stats_processor(request):
    s = Declaration.search()
    # res = s.params(search_type="count").aggs.metric(
    #     "distinct_names", "cardinality", field="full_name").execute()

    return {
        'total_declarations': s.count(),
        'total_persons': s.count()  # res.aggregations.distinct_names.value
    }
