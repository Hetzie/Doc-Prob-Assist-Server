from rest_framework import generics, status

from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate
from .serializers import UserSerializer


class LoginView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):

        user_data = authenticate(
            username=request.data['username'], password=request.data['password'])

        if user_data:
            token, created = Token.objects.get_or_create(user=user_data)
            return Response({'message': 'Login Successful!', 'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=401)


class UserListView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()


class EmailVerifyAPIView(generics.GenericAPIView):

    def get(self, request, token):
        try:
            user = Token.objects.get(key=token).user
            user.is_verified = True
            user.save()
            return Response()
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ForgotPassword(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()

    def post(self, request):
        if request.data.get("email") != None and request.data.get("password") != None:
            user = get_user_model().objects.get(email=request.data.get("email"))
            user.set_password(request.data.get("password"))
            user.save()
            return Response(data={"message": "Your password has been successfully changed."})
        return Response(data={"error": "Password change unsuccessful. Please try again later."})


class UserGetAPIView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ChangeUserStatus(generics.UpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()


class DeleteUserAPIView(generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
