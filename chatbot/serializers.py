from rest_framework import serializers
from .models import Chat, Query, Document, GoodResponse, BadResponse
import os
import json


class QuerySerializer(serializers.ModelSerializer):

    time = serializers.DateTimeField(format='%d-%m-%y')

    class Meta:
        model = Query
        fields = "__all__"


class ChatSerializer(serializers.ModelSerializer):

    queries = QuerySerializer(many=True, read_only=True)
    reference = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = "__all__"

    def get_reference(self, obj):
        # print(os.listdir())
        if os.path.exists(f'references/{obj.id}.json'):
            data = json.load(open(f'references/{obj.id}.json', 'r'))
            return data
        return []


class DocumentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Document
        fields = "__all__"


class GoodResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodResponse
        fields = "__all__"


class BadResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = BadResponse
        fields = "__all__"
