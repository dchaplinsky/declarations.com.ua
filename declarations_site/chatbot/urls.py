from django.conf.urls import url
from chatbot import views as chatbot_views


urlpatterns = [
    url(r'messages', chatbot_views.messages, name='chatbot_messages')
]
