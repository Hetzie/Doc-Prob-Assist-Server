from django.shortcuts import render
from rest_framework import generics, status
from datetime import datetime
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .serializers import (ChatSerializer, QuerySerializer,
                          Chat, Query, GoodResponse, BadResponse, Document, DocumentSerializer)


# Chats
class ChatListApiView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()


class ChatUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()


class ChatListByUser(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()

    def list(self, request):
        queryset = self.get_queryset().filter(user=request.user)
        serializer = ChatSerializer(queryset, many=True)
        return Response(serializer.data)

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


def temp_llm_ans(chat_id, doc_id, question):
    doc_name = 'test'
    doc_url = 'test'
    if doc_id != None:
        doc_obj = Document.objects.get(pk=doc_id)
        doc_name = doc_obj.name
        doc_url = f'media/{doc_name}/{doc_obj.file.name}'
    return True, {'answer': 'the answer will be here.',
                  'context': 'context here',
                  'reference': [{'doc_name': doc_name,
                                 'doc_url': doc_url,
                                 'pg_no': 12}]}


def regenerate_ans(question, context):
    doc_name = 'test'
    doc_url = 'test'
    return True, {'answer': 'the regenerated answer will be here.',
                  'context': 'context here',
                  'reference': [{'doc_name': doc_name,
                                 'doc_url': doc_url,
                                 'pg_no': 12}]}


class CreateAnswerApiView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        chat_id = request.data.get("chat_id")
        doc_id = request.data.get("doc_id")
        question = request.data.get("question")
        time = datetime.now()

        status, response = temp_llm_ans(chat_id, doc_id, question)
        chat = Chat.objects.get(pk=chat_id)
        doc = Document.objects.get(pk=doc_id)

        query_obj = Query.objects.create(chat=chat, question=question, response=response['answer'],
                                         time=time, context=response['context'], doc_id=doc)
        if status == False:
            return Response(status=400, data={'error': 'Not able to generate answer. Please try again later.'})
        return Response(status=200,
                        data={'query_id': query_obj.pk, 'chat_id': chat_id, 'doc_id': doc_id,
                              'question': question, 'answer': query_obj.response,
                              'time': time, 'refrence': response['reference']})


class RegenerateAnswerApiView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(seld, request):
        query_id = request.data.get('query_id')

        query_obj = Query.objects.get(pk=query_id)
        question = query_obj.question
        context = query_obj.context
        chat_id = query_obj.chat.pk
        time = datetime.now()
        doc_id = query_obj.doc_id.pk

        status, response = regenerate_ans(question, context)
        query_obj.response = response['answer']
        query_obj.save()
        if status == False:
            return Response(status=400, data={'error': 'Not able to generate answer. Please try again later.'})
        return Response(status=200,
                        data={'query_id': query_id, 'chat_id': chat_id, 'doc_id': doc_id,
                              'question': question, 'answer': response['answer'],
                              'time': time, 'refrence': response['reference']})


class GoodResponseApiView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query_id = request.data.get('query_id')

        query_obj = Query.objects.get(pk=query_id)
        question = query_obj.question
        response = query_obj.response

        GoodResponse.objects.create(question=question, response=response)

        return Response(data={"message": "Thank you! Your response has been saved."}, status=status.HTTP_201_CREATED)


class BadresponseApiView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query_id = request.data.get('query_id')
        feedback = request.data.get('feedback')
        expected_answer = request.data.get('expected_answer')

        query_obj = Query.objects.get(pk=query_id)
        question = query_obj.question
        response = query_obj.response

        BadResponse.objects.create(
            question=question, response=response, feedback=feedback, expected_answer=expected_answer)

        return Response(data={"message": "Thank you! Your response has been saved."}, status=status.HTTP_201_CREATED)

# Document


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

        return super().patch(request, *args, **kwargs)
