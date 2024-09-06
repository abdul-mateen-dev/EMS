from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db.models import Sum
from leave.models import  LeaveCategory, Leave




class LeaveCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveCategory
        fields = "__all__"


class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = ["user", "leave_type", "status", "start_date", "end_date", "leave_days", "total_leaves"]
        read_only_fields = ["user", "status",]

    def validate(self, data):
        user = self.context["request"].user
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        category = data.get("leave_type")
        print(category.id)


        if Leave.objects.filter(user=user,status="P").exists():
            raise ValidationError(f"There is already a pending leave .")

        if not start_date or not end_date:
            raise ValidationError("Both start date and end date must be provided.")

        leave_days = (end_date - start_date).days + 1  # Include the end date in the count

        if leave_days <= 0:
            raise ValidationError("End date must be after the start date.")

        # Checking we are out of range or not
        max_leaves = LeaveCategory.objects.aggregate(total=Sum("allowed_leaves"))["total"]
        total_leaves = Leave.objects.filter(user=user).aggregate(total=Sum("leave_days"))["total"] or 0

        if max_leaves < total_leaves+leave_days:
            raise ValidationError(f"You are out of range. You can only {max_leaves-total_leaves} days of leave.")
        consecutive_category_leave = LeaveCategory.objects.filter(id=category.id).aggregate(total=Sum("allowed_leaves"))["total"]
        if leave_days > consecutive_category_leave :
            raise ValidationError(f"You can not take more than {consecutive_category_leave} days of leave. ")

        # Checking category_leaves limit and consecutive leaves

        category_leaves = Leave.objects.filter(user=user,leave_type=category).aggreate(total=Sum("leave_days"))["total"] or 0
        category_allowed_leaves = LeaveCategory.objects.get(id=category.id).allowed_leaves
        if category_leaves >=category_allowed_leaves :
            raise ValidationError(f"You are out of range. You can only {category_allowed_leaves-category_leaves} days of leave")

        return data


class DashBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = "__all__"
        read_only_fields = ["user", "status", "leave_days", "total_leaves","start_date","end_date","leave_days","total_leaves"]
    