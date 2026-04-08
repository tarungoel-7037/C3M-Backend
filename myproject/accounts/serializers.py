from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from accounts.models import LawFirm
from myproject.constants import ErrorMessage


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, trim_whitespace=True)
    email = serializers.EmailField(trim_whitespace=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, default='', trim_whitespace=True, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, default='', trim_whitespace=True, allow_blank=True)
    group = serializers.CharField(max_length=150, trim_whitespace=True)
    law_firm_id = serializers.IntegerField(required=False, default=1)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(ErrorMessage.USERNAME_EXISTS)
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(ErrorMessage.EMAIL_EXISTS)
        return value

    def validate_group(self, value):
        allowed_groups = {'law_firm_user', 'law_firm_admin'}
        normalized = value.strip()
        if normalized not in allowed_groups:
            raise serializers.ValidationError('Group must be law_firm_user or law_firm_admin.')

        group = Group.objects.select_related('profile').filter(name=normalized).first()
        if not group:
            raise serializers.ValidationError(ErrorMessage.GROUP_NOT_FOUND)

        group_profile = getattr(group, 'profile', None)
        if not group_profile or group_profile.group_entity_type != 'law':
            raise serializers.ValidationError('Selected group is not a law firm group.')

        return normalized

    def validate_law_firm_id(self, value):
        if not LawFirm.objects.filter(id=value).exists():
            raise serializers.ValidationError('Law firm not found.')
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
