from django.contrib import admin
from chatbot.models import ChatHistory


class ChatHistoryAdmin(admin.ModelAdmin):
    search_fields = ('user__email', 'user__username', 'from_id', 'from_name', 'query')
    list_display = ('from_id', 'from_name', 'channel', 'query', 'answer', 'auto_reply', 'created')
    list_filter = ('auto_reply', 'created', )
    readonly_fields = ('user', )


admin.site.register(ChatHistory, ChatHistoryAdmin)
