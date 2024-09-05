from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db.models import Sum
from leave.models import Limitations, LeaveCategory, Leave


class LimitationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Limitations
        fields = "__all__"


class LeaveCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveCategory
        fields = "__all__"


class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = ["user", "leave_type", "status", "start_date", "end_date", "leave_days", "total_leaves"]
        read_only_fields = ["user", "status", "leave_days", "total_leaves"]

    def validate(self, data):
        user = self.context["request"].user
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if Leave.objects.filter(user=user,status="P").exists():
            raise ValidationError(f"There is already a pending leave .")

        if not start_date or not end_date:
            raise ValidationError("Both start date and end date must be provided.")

        leave_days = (end_date - start_date).days + 1  # Include the end date in the count

        if leave_days <= 0:
            raise ValidationError("End date must be after the start date.")

        limitations = Limitations.objects.latest("created_at")
        max_leaves = limitations.max_leaves
        consecutive_leaves = limitations.consecutive_leaves

        user = self.context['request'].user
        total_leaves = Leave.objects.filter(user=user).aggregate(total=Sum('leave_days'))['total'] or 0

        if leave_days > consecutive_leaves:
            raise ValidationError(f"Exceeds consecutive leave limit of {consecutive_leaves} days.")

        if total_leaves + leave_days > max_leaves:
            raise ValidationError(f"Total leave limit exceeded. You can take {max_leaves - total_leaves} more days.")

        return data


class DashBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = "__all__"
        read_only_fields = ["user", "status", "leave_days", "total_leaves","start_date","end_date","leave_days","total_leaves"]
