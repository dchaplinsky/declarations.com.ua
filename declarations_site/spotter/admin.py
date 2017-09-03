from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from spotter.models import SearchTask, TaskReport, NotifySend


class TaskRelatedLinksMixin(object):
    def user_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:auth_user_change", args=(obj.user.pk,)),
            obj.user.email
        ))
    user_link.short_description = 'User Link'

    def task_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:spotter_searchtask_change", args=(obj.task.pk,)),
            obj.task.query_title
        ))
    task_link.short_description = 'Task Link'


class SearchTaskAdmin(admin.ModelAdmin, TaskRelatedLinksMixin):
    search_fields = ('user__email', 'user__username', 'query')
    list_display = ('query_title', 'is_enabled', 'found_total', 'found_week', 'created', 'user_link')
    list_filter = ('is_enabled', 'is_deleted', 'created')
    readonly_fields = ('found_ids', 'user', 'user_link')


class TaskReportAdmin(admin.ModelAdmin, TaskRelatedLinksMixin):
    search_fields = ('task__user__email', 'task__user__username', 'task__query')
    list_display = ('created', 'task_link', 'found_total', 'found_new', 'user_link')
    list_filter = ('created',)
    readonly_fields = ('user', 'user_link', 'task', 'task_link', 'found_ids', 'new_ids')


class NotifySendAdmin(admin.ModelAdmin, TaskRelatedLinksMixin):
    search_fields = ('task__user__email', 'user__username', 'task__query', 'email')
    list_display = ('created', 'task_link', 'email', 'found_new', 'user_link')
    list_filter = ('created',)
    readonly_fields = ('user_link', 'task', 'task_link', 'new_ids')


admin.site.register(SearchTask, SearchTaskAdmin)
admin.site.register(TaskReport, TaskReportAdmin)
admin.site.register(NotifySend, NotifySendAdmin)
