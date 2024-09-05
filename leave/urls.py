from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import SetLimit, LeaveViewSet,LeaveCategoryView
from.dashboard import DashBoardView,approve,reject

router = DefaultRouter()

router.register("limit", SetLimit, basename="set_limit")
router.register("leave", LeaveViewSet, basename="leave")
router.register("dashboard", DashBoardView, basename="dashboard")
router.register("leave_category", LeaveCategoryView, basename="category")

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/leave/approve/<int:pk>/", approve, name="approve"),
    path("api/leave/reject/<int:pk>/", reject, name="reject"),

]
