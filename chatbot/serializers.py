from rest_framework import serializers
from .models import Chat, Query, Document, GoodResponse, BadResponse


class ChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chat
        fields = "__all__"


class QuerySerializer(serializers.ModelSerializer):

    class Meta:
        model = Query
        fields = "__all__"


class DocumentSerializer(serializers.ModelSerializer):

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
