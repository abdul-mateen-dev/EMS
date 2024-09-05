from django.db import models


class LeaveCategory(models.Model):
    name = models.CharField(max_length=50)
    allowed_leaves = models.PositiveIntegerField()
    is_short_leave = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
