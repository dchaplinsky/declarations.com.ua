from time import time
from hashlib import md5
from datetime import datetime
from django.urls import reverse
from django.conf import settings
from django.http import Http404, HttpResponse, QueryDict
from django.utils.http import http_date
from django.utils.dateparse import parse_date
from django.utils.feedgenerator import Atom1Feed, Rss201rev2Feed, Enclosure
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.syndication.views import add_domain


def urlencode(kwargs):
    q = QueryDict('', mutable=True)
    q.update(kwargs)
    return q.urlencode()


def populate_feed(request, data, feed_type):
    # now available only for search results
    if 'query' not in data:
        raise Http404()

    current_site = get_current_site(request)

    args = request.GET.copy()
    args.pop('format')

    link = '{}?{}'.format(request.path, args.urlencode())
    link = add_domain(current_site.domain, link, request.is_secure())
    guid = md5(request.get_full_path().encode('utf-8')).hexdigest()

    try:
        query = data['query']
        count = data['results']['paginator']['count']
        object_list = data['results']['object_list']
    except KeyError:
        raise Http404()

    title = 'Декларації за запитом "{}"'.format(query[:60])
    subtitle = 'Всього знайдено {} декларацій'.format(count)

    if not query:
        title += " (з фільтрами)"
    elif data.get('deepsearch', False):
        title += " (шукати скрізь)"

    feed = feed_type(
        title=title,
        subtitle=subtitle,
        link=link,
        description=subtitle,
        language=settings.LANGUAGE_CODE,
        feed_url=add_domain(
            current_site.domain,
            request.get_full_path(),
            request.is_secure(),
        ),
        author_name=settings.RSS_AUTHOR_NAME,
        author_link=settings.RSS_AUTHOR_LINK,
        author_email=settings.RSS_AUTHOR_EMAIL,
        categories=['Декларації'],
        feed_copyright='Public domain',
        feed_guid=guid,
        ttl=settings.RSS_TTL
    )

    for item in object_list:
        try:
            item_id = item.get('id', '')
            if not item_id:
                item_id = item.get('meta', {}).get('id', '')
            general = item['general']
            full_name = general.get('full_name', '')
            if not full_name:
                full_name = '{} {} {}'.format(general['last_name'],
                            general['name'], general['patronymic'])
            post = general['post']
            region = post.get('region', '')
            office = post.get('office', '')
            intro = item['intro']
            year = intro.get('declaration_year', '')
            doc_type = intro.get('doc_type', '')
            declaration = item['declaration']
            doc_url = declaration.get('url', '')
            pubdate = declaration.get('date', '') or intro.get('date', '')
            if pubdate and not isinstance(pubdate, datetime):
                pubdate = parse_date(pubdate)
            else:
                pubdate = datetime.now()
            updateddate = datetime.now()
        except KeyError:
            continue

        url = ''
        if item_id:
            url = reverse('details', kwargs={'declaration_id': item_id})
            url = add_domain(current_site.domain, url)
        title = '{}, {}'.format(full_name, post.get('post'))
        description = '{}, {}, {}, {}'.format(year, doc_type, region, office)
        author_link = '{}?{}'.format(reverse('search'),
            urlencode({'q': full_name}))
        author_link = add_domain(current_site.domain, author_link)

        if doc_url:
            enclosure = Enclosure(doc_url, '', '')
            enclosures = [enclosure]
        else:
            enclosures = None

        feed.add_item(
            title=title,
            link=url,
            description=description,
            unique_id=url,
            unique_id_is_permalink='1',
            enclosures=enclosures,
            pubdate=pubdate,
            updateddate=updateddate,
            author_name=full_name,
            author_email='',
            author_link=author_link,
            categories=['Декларації'],
            item_copyright='Public domain'
        )

    return feed


def FeedResponse(request, data, feed_type):
    feedgen = populate_feed(request, data, feed_type)
    response = HttpResponse(content_type=feedgen.content_type)
    response['Last-Modified'] = http_date(time())
    feedgen.write(response, 'utf-8')
    return response


def Atom1FeedResponse(request, data):
    return FeedResponse(request, data, feed_type=Atom1Feed)


def RssFeedResponse(request, data):
    return FeedResponse(request, data, feed_type=Rss201rev2Feed)
