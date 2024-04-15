from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .serializers import (ChatSerializer, QuerySerializer,
                          Chat, Query, Document, DocumentSerializer, QueryFeedBack, QueryFeedBackSerializer)
from .service import QueryChain
from datetime import datetime
query_chain = QueryChain()

# Chats


class ChatListApiView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user)


class ChatUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()


# Query


class QueryListCreateApiView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = QuerySerializer
    queryset = Query.objects.all()


class QueryUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = QuerySerializer
    queryset = Query.objects.all()


class QueryListByChat(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = QuerySerializer
    queryset = Query.objects.all()

    def list(self, request, chat_id):
        queryset = self.get_queryset().filter(chat__id=chat_id)
        serializer = QuerySerializer(queryset, many=True)
        return Response(serializer.data)

# ---------------------------------------------------------------------------------------


class CreateAnswerApiView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        chat_id = request.data.get("id")
        doc_id = request.data.get("doc_id")
        question = request.data.get("query")
        time = datetime.now()

        query_response, context, reference = query_chain.resolve_query(
            chat_id, doc_id, question)

        query_obj = Query.objects.create(
            chat=chat_id, doc_id=doc_id, question=question,
            time=time, context=context, response=query_response)

        query_obj = QuerySerializer(query_obj)
        return Response(data={
            "query": query_obj.data,
            "references": reference,
        })


class RegenerateAnswerApiView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(seld, request):
        query_id = request.data.get('query_id')
        query_obj = Query.objects.get(pk=query_id)
        query_response = query_chain.regenerate_answer(query_obj.context)
        query_obj.response = query_response
        query_obj.save()
        return Response(QuerySerializer(query_obj).data)


class DocumentUploadApiView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def get_queryset(self):
        if self.request.query_params.get("isNotVerified"):
            return super().get_queryset().filter(isVerified=False)
        if self.request.query_params.get("embedded"):
            return super().get_queryset().filter(embeddingStatus=Document.COMPLETED)
        return super().get_queryset().filter(isVerified=True)

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        if request.user.is_superuser:
            request.data['isVerified'] = True
            request.data['embeddingStatus'] = Document.PENDING

            print('verified-', request.data.get('isVerified'),
                  'embedding status-', request.data.get('embeddingStatus'))

        return super().create(request, *args, **kwargs)


class DocumentUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def patch(self, request, *args, **kwargs):
        if request.data.get('isVerified') == True:
            request.data['embeddingStatus'] = Document.PENDING
        elif request.data.get('isVerified') == False:
            request.data['embeddingStatus'] = Document.NOT_APPROVED
        print(request.data)

        return super().patch(request, *args, **kwargs)


class FeedBackListCreateAPIView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = QueryFeedBack.objects.all()
    serializer_class = QueryFeedBackSerializer
