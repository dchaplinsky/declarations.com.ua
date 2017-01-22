from elasticsearch_dsl import Search

from .constants import CATALOG_INDICES


def stats_processor(request):
    s = Search(index=CATALOG_INDICES)
    # res = s.params(search_type="count").aggs.metric(
    #     "distinct_names", "cardinality", field="full_name").execute()

    return {
        'total_declarations': s.count(),
        'total_persons': s.count()  # res.aggregations.distinct_names.value
    }
