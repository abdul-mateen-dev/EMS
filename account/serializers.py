from .models import User

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["name", "email", "password", "username"]
        reads_only_fields = ["team_leader", "role"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, max_length=255)
    password = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ["email", "password"]


class PromoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["role","boss"]


class TeamLeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "email", "team_leader", "role"]
        read_only_fields = ["id", "name", "email", "role"]



