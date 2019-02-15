from django.conf.urls import url
from spotter import views as spotter_views


urlpatterns = [
    url(r'logout/$', spotter_views.silent_logout, name='logout'),
    url(r'login-menu/$', spotter_views.login_menu, name='login_menu'),
    url(r'edit-email/$', spotter_views.edit_email, name='edit_email'),
    url(r'confirm-email/$', spotter_views.confirm_email, name='confirm_email'),
    url(r'login-via-email/$', spotter_views.login_via_email, name='login_via_email'),
    url(r'send-login-email/$', spotter_views.send_login_email, name='send_login_email'),
    url(r'deauthorize/$', spotter_views.deauthorize, name='deauthorize'),
    url(r'save-search/$', spotter_views.save_search, name='save_search'),
    url(r'search-list/$', spotter_views.search_list, name='search_list'),
    url(r'edit-search/(?P<task_id>\d+)/$', spotter_views.edit_search, name='edit_search'),
]
