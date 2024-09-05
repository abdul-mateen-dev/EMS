from django.contrib.auth import get_user_model

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


from .models import Leave
from .serializer import DashBoardSerializer


User = get_user_model()

class DashBoardView(ModelViewSet):
    serializer_class = DashBoardSerializer
    queryset = Leave.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = self.request.user

        def build_user_data(usr):
            """Helper function to build user data dictionary with serialized leave status data."""
            user_leaves = Leave.objects.filter(user=usr)

            pending_leaves = user_leaves.filter(status='P')
            approved_leaves = user_leaves.filter(status='A')
            rejected_leaves = user_leaves.filter(status='R')

            return {
                "id": usr.id,
                "username": usr.username,
                "email": usr.email,
                "name": usr.name,
                "pending_leaves": DashBoardSerializer(pending_leaves, many=True).data,
                "approved_leaves": DashBoardSerializer(approved_leaves, many=True).data,
                "rejected_leaves": DashBoardSerializer(rejected_leaves, many=True).data,
            }

        if user.is_admin():
            users = User.objects.all()
            data = [build_user_data(usr) for usr in users]
            return Response(data, status=status.HTTP_200_OK)

        elif user.is_supervisor():
            team_members = User.objects.filter(team_leader__email=user.email)
            my_leaves = Leave.objects.filter(user=user)
            serializer = DashBoardSerializer(my_leaves, many=True)
            data = [build_user_data(member) for member in team_members]

            response_data ={
                "data": data,
                "your_leaves": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        elif user.is_employee():
            data = build_user_data(user)
            return Response(data, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def approve(request, *args, **kwargs):
    pk = kwargs['pk']
    try:
        leave = Leave.objects.get(pk=pk,status='P')
    except Leave.DoesNotExist:
        return Response({"detail": "Leave not found it could not exists or it is already approved "}, status=status.HTTP_400_BAD_REQUEST)


    if leave.user.team_leader.email == request.user.email:
        leave.approve()
        return Response({"detail": "leave has been approved"}, status=status.HTTP_400_BAD_REQUEST)


    elif leave.user.role == 'SuperVisor':
        if leave.user.boss.email == request.user.email:
            leave.reject()
            return Response({"detail": "leave has been approved"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Permission Denied Only Admin Can Approve The Leave"},
                            status=status.HTTP_400_BAD_REQUEST)


    else:
        return Response({"error": "Permission Denied"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def reject(request, *args, **kwargs):
    pk = kwargs['pk']
    try:
        leave = Leave.objects.get(pk=pk, status='P')
    except Leave.DoesNotExist:
        return Response({"detail": "Leave not found."
                                   " It could not exists or it is already  rejected"},
                        status=status.HTTP_400_BAD_REQUEST)

    if leave.user.team_leader.email == request.user.email:
        leave.reject()
        return Response({"detail": "leave has been rejected"}, status=status.HTTP_400_BAD_REQUEST)


    elif leave.user.role == 'SuperVisor':
        if leave.user.boss.email == request.user.email:
            leave.reject()
            return Response({"detail": "leave has been rejected"}, status=status.HTTP_400_BAD_REQUEST)


        else:
            return Response({"error": "Permission Denied Only Admin Can Reject The Leave"}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({"error":"Permission Denied"}, status=status.HTTP_400_BAD_REQUEST)
