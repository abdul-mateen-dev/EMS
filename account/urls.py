from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import AdminView, LoginView, promotion, AssignTeamLeaderView, EmployeeView


router = DefaultRouter()
router.register("admin", AdminView, basename="admin")
router.register("login", LoginView, basename="login")
router.register("set_leader", AssignTeamLeaderView, basename="TeamLeader")
router.register("employee", EmployeeView, basename="Employee")
urlpatterns = [
    path("api/", include(router.urls)),
    path(
        "api/promotion/<int:pk>/", promotion, name="promotion"
    ),  # Corrected the path format
]
