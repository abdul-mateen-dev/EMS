from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "Admin"


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == "Employee" or request.user.role == "SuperVisor":
            return True
