from rest_framework import serializers


class SignupSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
