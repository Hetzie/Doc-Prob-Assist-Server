from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .serializers import (ChatSerializer, QuerySerializer,
                          Chat, Query, Document, DocumentSerializer, QueryFeedBack, QueryFeedBackSerializer, Directory, DirectorySerializer)
from datetime import datetime, timedelta
import requests
from django.conf import settings
from rest_framework.authentication import get_user_model


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
        r = requests.post('http://127.0.0.1:1235/retrive-doc/', data=(
            {'name': doc_id and doc.name, 'query': question}))
        context = r.json()['context']
        reference = r.json()['reference']
        r = requests.post('http://127.0.0.1:1236/resolve-query/', data=(
            {'query': context}))
        query_response = 'Two (2) regenerative tri-sector air pre-heaters (APHs) are provided for each unit.'

        query_obj = Query.objects.create(
            chat=Chat.objects.get(id=chat_id), doc_id=doc_id and doc, question=question,
            time=time, context=context, response=query_response, references=reference)

        query_obj = QuerySerializer(query_obj)
        return Response(data={
            "query": query_obj.data,
            "references": reference
        })


class RegenerateAnswerApiView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query_id = request.data.get('query_id')
        query_obj = Query.objects.get(pk=query_id)
        question = query_obj.question
        # API Request
        r = requests.post('http://127.0.0.1:1236/resolve-query/', data=(
            {'query': question}))
        query_response = r.json()['answer']
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

    def get(self, request, *args, **kwargs):
        data = self.get_queryset()
        serializer_obj = self.get_serializer_class()(data, many=True)
        return Response(serializer_obj.data)

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
            post_files = {
                "file": (doc.file.path, open(doc.file.path, "rb"), 'multipart/form-data')
            }
            # print(f'PATH :: {doc.file.url}')
            requests.post('http://127.0.0.1:1234/embedd-doc/', data=(
                {'name': doc.name, 'source': doc.file.url}), files=post_files)
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
            post_files = {
                "file": (doc.file.path, open(doc.file.path, "rb"), 'multipart/form-data')
            }
            # print(f'PATH :: {doc.file.url}')
            requests.post('http://127.0.0.1:1234/embedd-doc/', data=(
                {'name': doc.name, 'source': doc.file.url}), files=post_files)

        return response

    def delete(self, request, pk):
        doc = Document.objects.get(pk=pk)
        # API Request
        requests.delete('http://127.0.0.1:1234/delete-doc/', data=(
            {'name': doc.name, }), )
        return super().delete(request, pk)


class FeedBackListCreateAPIView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = QueryFeedBack.objects.all()
    serializer_class = QueryFeedBackSerializer


class EmbeddingStatusChangeAPIView(generics.GenericAPIView):

    def post(self, request):
        name = request.data.get('name')
        status = request.data.get('status')
        doc_obj = Document.objects.get(name=name)
        if status == Document.PROCESSING:
            doc_obj.embeddingStatus = Document.PROCESSING
        elif status == Document.COMPLETED:
            doc_obj.embeddingStatus = Document.COMPLETED
        doc_obj.save()
        return Response(DocumentSerializer(doc_obj).data)

# -------------------------------------------------------------------------------------------------------------------


class AnalyticsDataAPIView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        documents = Document.objects.all()
        total_documents = documents.count()
        embedded_docs = documents.filter(
            embeddingStatus=Document.COMPLETED).count()

        total_users = get_user_model().objects.count()

        total_questions = Query.objects.select_related('feedback')
        total_questions_count = total_questions.count()

        good_bad_resp = {'good_resp': 0, 'bad_resp': 0}

        for q in total_questions:
            try:
                rating = q.feedback.rating

            except:
                rating = 0

            if rating > 3:
                good_bad_resp['good_resp'] += 1
            elif rating != 0:
                good_bad_resp['bad_resp'] += 1

        last_date = datetime.now()
        first_date = last_date-timedelta(days=6)
        past_week_query = Query.objects.select_related('feedback').filter(
            time__range=(first_date, last_date)).order_by('time')
        weekly_total_questions = past_week_query.count()

        date_modified = first_date
        past_week_date = [first_date.date().strftime(format='%d %b')]

        while date_modified < last_date:
            date_modified += timedelta(days=1)
            past_week_date.append(
                date_modified.date().strftime(format='%d %b'))

        weekly_feedback = {}
        for date in past_week_date:
            weekly_feedback[date] = [0, 0, 0]
        for q in past_week_query:
            try:
                rating = q.feedback.rating

            except:
                rating = 0

            date = q.time.date().strftime(format='%d %b')

            if rating > 3:
                weekly_feedback[date][0] += 1
            elif rating == 0:
                weekly_feedback[date][1] += 1
            else:
                weekly_feedback[date][2] += 1

        return Response({'weekly_feedback': weekly_feedback, 'weekly_total_questions': weekly_total_questions,
                         'embedded_documents': embedded_docs, 'total_users': total_users, 'total_questions': total_questions_count,
                         'total_documents': total_documents,
                         'good_bad_response': good_bad_resp})


class DownloadFeedback(generics.GenericAPIView):
    queryset = QueryFeedBack.objects.all()

    def post(self, request):
        df = self.get_queryset().to_dataframe()
        df.to_csv("media/downloads/feedbacks.csv")
        return Response({"url": "media/downloads/feedbacks.csv"})


class DirectoryListCreateApiView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = DirectorySerializer
    queryset = Directory.objects.all()
