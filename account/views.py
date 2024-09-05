from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.core.serializers import serialize

User = get_user_model()
from .serializers import (
    UserSerializer,
    LoginSerializer,
    PromoteSerializer,
    TeamLeaderSerializer,

)
from .permission import IsAdmin

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)

from rest_framework_simplejwt.authentication import JWTAuthentication

from account.models import User, SuperVisor
from .serializers import PromoteSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    access_token = AccessToken.for_user(user)

    return {"access": str(access_token), "refresh": str(refresh)}


class AdminView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(role="Admin")
        token = get_tokens_for_user(user)
        data = (
            {
                "token": token,
                "message": "Registration Success",
                "data": serializer.data,
            },
        )
        return Response(
            data=data,
            status=status.HTTP_200_OK,
        )


class LoginView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = LoginSerializer
    authentication_classes = []
    permission_classes = []
    http_method_names = [
        "post",
    ]

    def create(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get("email")
            print(email)
            password = serializer.validated_data.get("password")
            print(password)
            user = authenticate(request, email=email, password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                return Response(
                    {"token": token, "message": "Login Successful"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"detail": "Invalid Credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsAdmin])
@authentication_classes([JWTAuthentication])
def promotion(request, pk=None):
    try:
        user = User.objects.get(id=pk)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = PromoteSerializer(user, data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(role="SuperVisor", boss=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class AssignTeamLeaderView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = TeamLeaderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,IsAdmin]

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = TeamLeaderSerializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)



class EmployeeView(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    http_method_names = ['post',]

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save(role="Employee")
            print(user)
            token = get_tokens_for_user(user)
            data = (
                {
                    "token": token,
                    "message": "Registration Success",
                    "data": serializer.data,
                },
            )
            return Response(
                data=data,
                status=status.HTTP_200_OK,
            )

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

