from rest_framework import serializers, exceptions
from rest_framework.authentication import get_user_model


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=30, min_length=8, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name',
                  'email', 'password', 'is_staff', 'is_active']

    # def validate(self, attrs):
    #     username = attrs.get('username', None)
    #     if username is None:
    #         raise serializers.ValidationError(
    #             'User Should Have username'
    #         )
    #     return attrs

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)
