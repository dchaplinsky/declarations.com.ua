from django.contrib import admin
from spotter.models import SearchTask, TaskReport, NotifySend


class SearchTaskAdmin(admin.ModelAdmin):
    search_fields = ('user__email', 'user__username', 'query')
    list_display = ('query', 'is_enabled', 'found_total', 'found_week', 'created', 'user')
    list_filter = ('is_enabled', 'is_deleted', 'created')
    readonly_fields = ('found_ids',)


class TaskReportAdmin(admin.ModelAdmin):
    search_fields = ('task__user__email', 'task__user__username', 'task__query')
    list_display = ('created', 'task', 'found_total', 'found_new', 'user')
    list_filter = ('created',)
    readonly_fields = ('user', 'task', 'found_ids', 'new_ids')


class NotifySendAdmin(admin.ModelAdmin):
    search_fields = ('task__user__email', 'user__username', 'task__query', 'email')
    list_display = ('created', 'task', 'email', 'found_new', 'user')
    list_filter = ('created',)
    readonly_fields = ('user', 'task', 'new_ids')


admin.site.register(SearchTask, SearchTaskAdmin)
admin.site.register(TaskReport, TaskReportAdmin)
admin.site.register(NotifySend, NotifySendAdmin)
