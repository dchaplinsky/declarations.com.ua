from django.contrib import admin
from chatbot.models import ChatHistory


class ChatHistoryAdmin(admin.ModelAdmin):
    search_fields = ('user__email', 'user__username', 'from_id', 'from_name', 'query')
    list_display = ('from_id', 'from_name', 'query', 'answer', 'created')
    list_filter = ('created', )
    readonly_fields = ('user', )


admin.site.register(ChatHistory, ChatHistoryAdmin)
