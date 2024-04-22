from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .serializers import (ChatSerializer, QuerySerializer,
                          Chat, Query, Document, DocumentSerializer, QueryFeedBack, QueryFeedBackSerializer)
from datetime import datetime

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
        if doc_id:
            doc = Document.objects.get(id=doc_id)
        # API Request
        query_response, context, reference = '', '', ''

        query_obj = Query.objects.create(
            chat=Chat.objects.get(id=chat_id), doc_id=doc_id and doc, question=question,
            time=time, context=context, response=query_response)

        query_obj = QuerySerializer(query_obj)
        return Response(data={
            "query": query_obj.data,
            "references": [
                {
                    "docName": "Parts_of_Speech",
                    "pageNumber": 8,
                    "url": "http://127.0.0.1:8000/media/docs/Parts_of_Speech___DPP_01_Discussion_Notes.pdf"
                }
            ],
        })


class RegenerateAnswerApiView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(seld, request):
        query_id = request.data.get('query_id')
        query_obj = Query.objects.get(pk=query_id)
        # API Request
        query_response = ''
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

        response = super().create(request, *args, **kwargs)
        if request.user.is_superuser:
            doc = Document.objects.get(pk=response.data['id'])
            # API Request
        return response


class DocumentUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def patch(self, request, pk, *args, **kwargs):
        if request.data.get('isVerified') == True:
            request.data['embeddingStatus'] = Document.PENDING
        elif request.data.get('isVerified') == False:
            request.data['embeddingStatus'] = Document.NOT_APPROVED

        response = super().patch(request, pk, *args, **kwargs)
        if request.data.get('isVerified') == True:
            # API Request
            doc = Document.objects.get(pk=pk)

        return response

    def delete(self, request, pk):
        doc = Document.objects.get(pk=pk)
        # API Request
        return super().delete(request, pk)


class FeedBackListCreateAPIView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = QueryFeedBack.objects.all()
    serializer_class = QueryFeedBackSerializer
