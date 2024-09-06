from django.template.context_processors import request
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from account.permission import IsAdmin, IsEmployee

from .serializer import  LeaveCategorySerializer, LeaveSerializer
from .models import LeaveCategory, Leave

from rest_framework_simplejwt.authentication import JWTAuthentication



class LeaveCategoryView(ModelViewSet):
    queryset = LeaveCategory.objects.all()
    serializer_class = LeaveCategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def perform_create(self, serializer):
       serializer.save()


class LeaveViewSet(ModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsEmployee]

    def get_queryset(self):
        return Leave.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        leave = self.get_object()
        if leave.status != "P":
            return Response({"error": "You can only update pending leaves"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(leave, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        leave = self.get_object()
        if leave.status != "P":
            return Response({"error": "You can only delete pending leaves"}, status=status.HTTP_400_BAD_REQUEST)

        leave.delete()
        return Response({"msg": "Leave deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        leaves = self.get_queryset()
        if not leaves.exists():
            return Response({"error": "No leaves found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = LeaveSerializer(leaves, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
