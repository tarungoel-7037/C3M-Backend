from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from myproject.constants import ErrorMessage


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, trim_whitespace=True)
    email = serializers.EmailField(trim_whitespace=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, default='', trim_whitespace=True, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, default='', trim_whitespace=True, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(ErrorMessage.USERNAME_EXISTS)
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(ErrorMessage.EMAIL_EXISTS)
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': [ErrorMessage.PASSWORD_MISMATCH]})
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
        )
        try:
            validate_password(data['password'], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': list(exc.messages)})
        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(trim_whitespace=True)
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


# ── Output serializers for the profile endpoint ───────────────────────────────

class GroupOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    display_name = serializers.CharField()
    group_entity_type = serializers.CharField()
    permissions = serializers.ListField(child=serializers.CharField())


class LawFirmAccessOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    group = GroupOutputSerializer()


class OrganisationAccessOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    group = GroupOutputSerializer()


class UserProfileOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    contact_number = serializers.CharField(allow_null=True)
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    law_firms = LawFirmAccessOutputSerializer(many=True)
    organisations = OrganisationAccessOutputSerializer(many=True)
    is_law_firm_admin = serializers.BooleanField()
    permissions = serializers.ListField(child=serializers.CharField())
    created_at = serializers.CharField(allow_null=True)
    updated_at = serializers.CharField(allow_null=True)
