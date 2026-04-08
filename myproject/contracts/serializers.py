from django.contrib.auth.models import User
from rest_framework import serializers

from accounts.models import LawFirm, Organisation
from myapp.models import (
    ContractsContract,
    ContractsContractdocument,
    MastersContractroletype,
    MastersContracttype,
    MastersDocumenttype,
    ObligationsEscalationmatrix,
)

PUBLISHED_REQUIRED_FIELDS = [
    'project_title', 'contract_type', 'project_value',
    'start_date', 'end_date', 'site_address_line_1',
    'site_city', 'site_state', 'site_zip_code',
]

STATUS_CHOICES = ['draft', 'pending', 'in_progress', 'completed']
OBLIGATION_STATUS_CHOICES = ['pending', 'in_progress', 'completed']


class ContractCreateSerializer(serializers.Serializer):
    # Always required
    organisation = serializers.IntegerField()
    law_firm = serializers.IntegerField()

    # Optional, defaults to draft
    status = serializers.ChoiceField(choices=STATUS_CHOICES, default='draft')

    # Required when status != draft
    project_title = serializers.CharField(max_length=255, required=False, allow_blank=False)
    contract_type = serializers.IntegerField(required=False, allow_null=True)
    project_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    site_address_line_1 = serializers.CharField(max_length=500, required=False, allow_blank=False)
    site_city = serializers.CharField(max_length=100, required=False, allow_blank=False)
    site_state = serializers.CharField(max_length=100, required=False, allow_blank=False)
    site_zip_code = serializers.CharField(max_length=20, required=False, allow_blank=False)

    # Optional
    counter_party = serializers.CharField(max_length=255, required=False, allow_blank=True)
    site_address_line_2 = serializers.CharField(max_length=500, required=False, allow_blank=True)
    site_country = serializers.CharField(max_length=2, required=False, allow_blank=True)
    contract_parent_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_organisation(self, value):
        if not Organisation.objects.filter(id=value).exists():
            raise serializers.ValidationError('Organisation not found.')
        return value

    def validate_law_firm(self, value):
        if not LawFirm.objects.filter(id=value).exists():
            raise serializers.ValidationError('Law firm not found.')
        return value

    def validate_contract_type(self, value):
        if value is not None and not MastersContracttype.objects.filter(id=value).exists():
            raise serializers.ValidationError('Contract type not found.')
        return value

    def validate(self, data):
        status = data.get('status', 'draft')

        if status != 'draft':
            missing = [f for f in PUBLISHED_REQUIRED_FIELDS if not data.get(f)]
            if missing:
                raise serializers.ValidationError({
                    field: 'This field is required when status is not draft.'
                    for field in missing
                })

        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({'end_date': 'end_date must be after start_date.'})

        project_title = data.get('project_title')
        law_firm_id = data.get('law_firm')
        if project_title and law_firm_id:
            if ContractsContract.objects.filter(
                project_title__iexact=project_title,
                law_firm_id=law_firm_id
            ).exists():
                raise serializers.ValidationError({
                    'project_title': 'A contract with this title already exists for this law firm.'
                })

        return data


class EscalationMatrixInputSerializer(serializers.Serializer):
    level = serializers.IntegerField(min_value=1)
    role_id = serializers.IntegerField()
    days = serializers.IntegerField(min_value=1)

    def validate_role_id(self, value):
        if not MastersContractroletype.objects.filter(id=value).exists():
            raise serializers.ValidationError('Role not found.')
        return value


class ObligationBaseSerializer(serializers.Serializer):
    obligation_title = serializers.CharField(max_length=255, required=False, allow_blank=False)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    assigned_role = serializers.IntegerField(required=False)
    extend_timeline_approval = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    obligation_type = serializers.CharField(max_length=50, required=False, allow_blank=False)
    obligation_document = serializers.IntegerField(required=False, allow_null=True)
    page_section_reference = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=OBLIGATION_STATUS_CHOICES, required=False, default='pending')
    escalation_matrix = EscalationMatrixInputSerializer(many=True, required=False)
    party_type = serializers.CharField(max_length=50, required=False, allow_blank=False, default='organisation')

    def validate_assigned_role(self, value):
        if not MastersContractroletype.objects.filter(id=value).exists():
            raise serializers.ValidationError('Assigned role not found.')
        return value

    def validate_obligation_document(self, value):
        if value is None:
            return value

        contract_id = self.context.get('contract_id')
        if not ContractsContractdocument.objects.filter(id=value, contract_id=contract_id).exists():
            raise serializers.ValidationError('Obligation document not found for this contract.')
        return value


class ObligationCreateSerializer(ObligationBaseSerializer):
    obligation_title = serializers.CharField(max_length=255)
    assigned_role = serializers.IntegerField()
    obligation_type = serializers.CharField(max_length=50)

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({'end_date': 'end_date must be greater than or equal to start_date.'})

        return data


class ObligationUpdateSerializer(ObligationBaseSerializer):
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        instance = self.context.get('instance')

        if instance:
            if 'start_date' not in self.initial_data:
                start_date = instance.start_date
            if 'end_date' not in self.initial_data:
                end_date = instance.end_date

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({'end_date': 'end_date must be greater than or equal to start_date.'})

        return data


class ObligationOutputSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'obligation_title': instance.obligation_title,
            'description': instance.description,
            'assigned_role': self._get_role_data(instance.assigned_role_id),
            'obligation_document': self._get_document_data(instance.obligation_document_id),
            'page_section_reference': instance.page_section_reference,
            'extend_timeline_approval': instance.extend_timeline_approval,
            'obligation_type': instance.obligation_type,
            'start_date': instance.start_date,          
            'end_date': instance.end_date,
            'status': instance.status,
            'escalation_matrix': self._get_escalation_data(instance.id),
            'created_at': instance.created_at,
        }

    def _get_role_data(self, role_id):
        if not role_id:
            return None

        role = MastersContractroletype.objects.filter(id=role_id).first()
        if not role:
            return None

        return {
            'id': role.id,
            'role_name': role.role_name,
            'display_name': role.display_name,
            'description': role.description,
        }

    def _get_document_data(self, document_id):
        if not document_id:
            return None

        document = ContractsContractdocument.objects.filter(id=document_id).first()
        if not document:
            return None

        document_type = MastersDocumenttype.objects.filter(id=document.document_type_id).first()
        uploaded_by = User.objects.filter(id=document.uploaded_by_id).first()

        return {
            'id': document.id,
            'document_name': document.document_name,
            'document_type': {
                'id': document_type.id,
                'name': document_type.name,
            } if document_type else None,
            'file_url': document.file_path,
            'uploaded_by': {
                'id': uploaded_by.id,
                'full_name': ' '.join(filter(None, [uploaded_by.first_name, uploaded_by.last_name])) or uploaded_by.username,
                'email': uploaded_by.email,
            } if uploaded_by else None,
            'uploaded_at': document.created_at,
        }

    def _get_escalation_data(self, obligation_id):
        escalations = ObligationsEscalationmatrix.objects.filter(
            obligation_id=obligation_id,
            deleted_at__isnull=True,
        ).order_by('level', 'id')

        data = []
        for escalation in escalations:
            data.append({
                'id': escalation.id,
                'level': escalation.level,
                'role': self._get_role_data(escalation.notify_role_id),
                'days': escalation.days,
                'is_triggered': escalation.is_triggered,
                'triggered_at': escalation.triggered_at,
            })

        return data
