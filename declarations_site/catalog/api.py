from functools import wraps

from elasticsearch_dsl.response import Response
from elasticsearch_dsl.utils import AttrDict, AttrList, ObjectBase

from django.http import JsonResponse
from django.http.response import HttpResponseBase
from django.shortcuts import render

from .rss import Atom1FeedResponse, RssFeedResponse


def serialize_for_api(data, new_api=False, sections=None):
    """Transform complex types that we use into simple ones recursively.
    Note: recursion isn't followed when we know that transformed types aren't
    supposed to contain any more complex types.

    TODO: this is rather ugly, would look better if views/models defined
    transformations explicitly. This is hard to achieve with function-based
    views, so it's pending a CBV move."""
    if hasattr(data, 'to_api'):
        return serialize_for_api(data.to_api(), new_api=new_api, sections=sections)
    elif isinstance(data, Response):
        return serialize_for_api(data.hits._l_, new_api=new_api, sections=sections)
    elif isinstance(data, (AttrDict, ObjectBase)):
        if new_api and hasattr(data, "api_response"):
            return data.api_response(fields=sections)
        else:
            res = data.to_dict()
            if hasattr(data, 'meta'):
                res['id'] = data.meta.id
            return res
    elif isinstance(data, AttrList):
        return data._l_
    elif isinstance(data, dict):
        return {
            k: serialize_for_api(v, new_api=new_api, sections=sections)
            for k, v in data.items()
        }
    elif isinstance(data, (list, tuple, set)):
        return list(map(lambda x: serialize_for_api(
            x, new_api=new_api, sections=sections), data)
        )
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
            if isinstance(context, HttpResponseBase):
                return context

            fmt = request.GET.get('format', 'html')
            sections = request.GET.getlist('section', None)
            if not sections:
                sections = None

            if fmt == 'json':
                return JsonResponse(serialize_for_api(context), safe=False)
            elif fmt == 'atom':
                return Atom1FeedResponse(request, serialize_for_api(context))
            elif fmt == 'rss':
                return RssFeedResponse(request, serialize_for_api(context))
            elif fmt == 'opendata':
                return JsonResponse(
                    serialize_for_api(context, new_api=True, sections=sections),
                    safe=False
                )
            else:
                return render(request, template_name, context)
        return func_wrapper
    return hybrid_decorator
