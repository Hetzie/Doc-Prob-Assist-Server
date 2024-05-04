from rest_framework import serializers
from .models import Chat, Query, Document, QueryFeedBack, Directory
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


class QueryFeedBackSerializer(serializers.ModelSerializer):
    question = serializers.ReadOnlyField(source='query.question')
    answer = serializers.ReadOnlyField(source='query.response')
    username = serializers.ReadOnlyField(source='user.username')

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    class Meta:
        model = QueryFeedBack
        fields = "__all__"


class DirectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Directory
        fields = "__all__"
