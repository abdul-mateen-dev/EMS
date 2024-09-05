from django.db import models
from account.models import User
from .leave_category import LeaveCategory


class Leave(models.Model):
    STATUS_CHOICES = (
        ("P", "Pending"),
        ("A", "Approved"),
        ("R", "Rejected"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveCategory, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="P")
    total_leaves = models.IntegerField(default=0, null=True, blank=True)
    leave_days = models.IntegerField(default=0, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.leave_days = (self.end_date - self.start_date).days + 1  # Including end date in leave days
        current_total_leaves = Leave.objects.filter(user=self.user).aggregate(total=models.Sum('leave_days'))['total'] or 0
        self.total_leaves = current_total_leaves + self.leave_days
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.name}, {self.leave_type.name}"


    def approve(self):
        self.status = "A"
        self.save()

    def reject(self):
        self.status = "R"
        self.save()