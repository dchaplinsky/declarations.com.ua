from functools import wraps

from elasticsearch_dsl.result import Response
from elasticsearch_dsl.utils import AttrDict, AttrList, ObjectBase

from django.http import JsonResponse
from django.shortcuts import render


def serialize_for_api(data):
    """Transform complex types that we use into simple ones recursively.
    Note: recursion isn't followed when we know that transformed types aren't
    supposed to contain any more complex types.

    TODO: this is rather ugly, would look better if views/models defined
    transformations explicitly. This is hard to achieve with function-based
    views, so it's pending a CBV move."""
    if hasattr(data, 'to_api'):
        return serialize_for_api(data.to_api())
    elif isinstance(data, Response):
        return serialize_for_api(data.hits._l_)
    elif isinstance(data, (AttrDict, ObjectBase)):
        return data.to_dict()
    elif isinstance(data, AttrList):
        return data._l_
    elif isinstance(data, dict):
        return {k: serialize_for_api(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return list(map(serialize_for_api, data))
    return data


def hybrid_response(template_name):
    """Returns either an HTML or JSON representation of the data that
    decorated function generates. Decision on format is based on "format" param
    in the query string, default is "html". For JSON serialization the data
    is passed through a recursive transformation into simple types.

    TODO: This would look better as a mixin for CBVs."""
    def hybrid_decorator(func):
        @wraps(func)
        def func_wrapper(request, *args, **kwargs):
            context = func(request, *args, **kwargs)
            if request.GET.get('format', 'html') == 'json':
                return JsonResponse(serialize_for_api(context), safe=False)
            else:
                return render(request, template_name, context)
        return func_wrapper
    return hybrid_decorator
