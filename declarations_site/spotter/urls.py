from django.conf.urls import url
from spotter import views as spotter_views


urlpatterns = [
    url(r'logout/$', spotter_views.silent_logout, name='logout'),
    url(r'save-search/$', spotter_views.save_search, name='save_search'),
    url(r'search-list/$', spotter_views.search_list, name='search_list'),
    url(r'toggle-task/(?P<task_id>\d+)/(?P<task_status>\w+)/$',
        spotter_views.toggle_task, name='toggle_task'),
    url(r'delete-task/(?P<task_id>\d+)/$',
        spotter_views.delete_task, name='delete_task'),
]
