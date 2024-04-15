from django.urls import path
from .views import (
    ChatListApiView, ChatUpdateDeleteApiView, QueryListCreateApiView,
    QueryUpdateDeleteApiView, QueryListByChat, CreateAnswerApiView, RegenerateAnswerApiView, DocumentUploadApiView, DocumentUpdateDeleteApiView)

urlpatterns = [
    path('chats/', ChatListApiView.as_view()),
    path('edit_chats/<int:pk>', ChatUpdateDeleteApiView.as_view()),
    path('add_query/', QueryListCreateApiView.as_view()),
    path('edit_query/<int:pk>', QueryUpdateDeleteApiView.as_view()),
    path('query/<int:chat_id>', QueryListByChat.as_view()),
    path('answer/', CreateAnswerApiView.as_view()),
    path('regenerate_answer/', RegenerateAnswerApiView.as_view()),
    path('doc/', DocumentUploadApiView.as_view()),
    path('update-doc/<int:pk>', DocumentUpdateDeleteApiView.as_view()),
]
