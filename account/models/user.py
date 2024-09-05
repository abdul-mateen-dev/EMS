
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email


class User(AbstractUser):
    Choices = (
        ("Admin", "Admin"),
        ("Employee", "Employee"),
        ("SuperVisor", "SuperVisor"),
    )

    last_name = None
    first_name = None

    email = models.EmailField(unique=True, validators=[validate_email])

    role = models.CharField(max_length=50, choices=Choices, default="Employee")
    name = models.CharField(max_length=120)
    updated_at = models.DateTimeField(auto_now=True)
    team_leader = models.ForeignKey(
        "account.SuperVisor", null=True, blank=True, on_delete=models.SET_NULL
    )
    boss = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "username"]

    def __str__(self):
        return self.name

    def is_admin(self):
        return self.role == "Admin"

    def is_employee(self):
        return self.role == "Employee"

    def is_supervisor(self):
        return self.role == "SuperVisor"
