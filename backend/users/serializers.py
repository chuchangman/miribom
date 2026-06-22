from rest_framework import serializers


class SignupSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ProfileUpdateSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=50, required=False)
    profile_image_url = serializers.CharField(max_length=512, required=False, allow_blank=True)


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)


class LivingUpdateSerializer(serializers.Serializer):
    housing_type = serializers.CharField(max_length=20, required=False, allow_blank=True)
    area_size = serializers.IntegerField(required=False, allow_null=True, min_value=1)
