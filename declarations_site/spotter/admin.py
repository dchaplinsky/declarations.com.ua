from django.contrib import admin
from spotter.models import SearchTask, TaskReport, NotifySend


class SearchTaskAdmin(admin.ModelAdmin):
    search_fields = ('user__email', 'user__username', 'query')
    list_display = ('query', 'is_enabled', 'found_total', 'found_week', 'create_date', 'user')


class TaskReportAdmin(admin.ModelAdmin):
    search_fields = ('task__user__email', 'task__user__username', 'task__query')
    list_display = ('create_date', 'task', 'found_total', 'found_new', 'user')
    readonly_fields = ('user', 'task')


class NotifySendAdmin(admin.ModelAdmin):
    search_fields = ('task__user__email', 'user__username', 'task__query', 'email')
    list_display = ('create_date', 'task', 'email', 'user')
    readonly_fields = ('user', 'task')


admin.site.register(SearchTask, SearchTaskAdmin)
admin.site.register(TaskReport, TaskReportAdmin)
admin.site.register(NotifySend, NotifySendAdmin)
