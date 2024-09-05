from django.db import models
from django.core.validators import validate_email
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model


@receiver(pre_save, sender="account.User")

def manage_supervisor_instance(sender, instance, **kwargs):
    User = get_user_model()
    if instance.pk:
        previous_user = User.objects.get(pk=instance.pk)
        if previous_user.role == "SuperVisor" and instance.role != "SuperVisor":
            try:
                supervisor = SuperVisor.objects.get(email=instance.email)
                supervisor.delete()
            except SuperVisor.DoesNotExist:
                pass
        elif previous_user.role != "SuperVisor" and instance.role == "SuperVisor":
            SuperVisor.objects.create(
                email=instance.email,
                username=instance.username,
                role=instance.role,
                name=instance.name,
            )
    else:
        if instance.role == "SuperVisor":
            SuperVisor.objects.create(
                email=instance.email,
                username=instance.username,
                role=instance.role,
                name=instance.name,
            )


class SuperVisor(models.Model):
    email = models.EmailField(unique=True, validators=[validate_email])
    role = models.CharField(max_length=10)
    name = models.CharField(max_length=120)
    boss = models.ForeignKey("account.User", on_delete=models.CASCADE,null=True,blank=True)
    username = models.CharField(max_length=120)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
