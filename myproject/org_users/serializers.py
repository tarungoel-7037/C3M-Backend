from django.contrib.auth.models import Group, User
from rest_framework import serializers

from accounts.models import Organisation
from myproject.constants import ErrorMessage


class AddOrganisationUserSerializer(serializers.Serializer):
    email = serializers.EmailField(trim_whitespace=True)
    full_name = serializers.CharField(required=True, trim_whitespace=True) 

    first_name = serializers.CharField(max_length=150, required=False, default='', allow_blank=True, trim_whitespace=True)
    last_name = serializers.CharField(max_length=150, required=False, default='', allow_blank=True, trim_whitespace=True)

    organisation_id = serializers.IntegerField()
    group_id = serializers.IntegerField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(ErrorMessage.EMAIL_EXISTS)
        return value.lower()

    def validate_organisation_id(self, value):
        if not Organisation.objects.filter(id=value).exists():
            raise serializers.ValidationError(ErrorMessage.ORGANISATION_NOT_FOUND)
        return value

    def validate_group_id(self, value):
        if not Group.objects.filter(id=value).exists():
            raise serializers.ValidationError(ErrorMessage.GROUP_NOT_FOUND)
        return value

    def validate_group_id(self, value):
        if not Group.objects.filter(id=value).exists():
            raise serializers.ValidationError(ErrorMessage.GROUP_NOT_FOUND)
        return value


class UpdateOrganisationUserSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=False, trim_whitespace=True) 

    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True, trim_whitespace=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, trim_whitespace=True)

    organisation_id = serializers.IntegerField(required=False)
    group_id = serializers.IntegerField(required=False)

    def validate_group_id(self, value):
        if not Group.objects.filter(id=value).exists():
            raise serializers.ValidationError(ErrorMessage.GROUP_NOT_FOUND)
        return value

    def validate_organisation_id(self, value):
        if not Organisation.objects.filter(id=value).exists():
            raise serializers.ValidationError(ErrorMessage.ORGANISATION_NOT_FOUND)
        return value


class OrganisationUserSerializer(serializers.ModelSerializer):
    """Output serializer for a user — matches the standard user list response shape."""
    full_name = serializers.SerializerMethodField()
    contact_number = serializers.SerializerMethodField()
    law_firms = serializers.SerializerMethodField()
    organisations = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'contact_number', 'is_active', 'law_firms', 'organisations', 'created_at']

    def get_full_name(self, obj):
        return ' '.join(filter(None, [obj.first_name, obj.last_name])) or obj.username

    def get_contact_number(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.contact_number if profile else None

    def get_law_firms(self, obj):
        result = []
        for access in obj.law_firm_accesses.all():
            result.append({
                'id': access.law_firm.id,
                'name': access.law_firm.name,
                'group': {
                    'id': access.group.id,
                    'name': access.group.name,
                },
            })
        return result

    def get_organisations(self, obj):
        result = []
        for access in obj.organisation_accesses.all():
            result.append({
                'id': access.organisation.id,
                'name': access.organisation.name,
                'law_firm_id': access.organisation.law_firm.id,
                'law_firm_name': access.organisation.law_firm.name,
            })
        return result

    def get_created_at(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.created_at.isoformat() if profile else None
