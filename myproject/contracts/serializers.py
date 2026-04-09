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
    ObligationsObligation,
    MastersTasktype,
    TasksContracttask,
    TasksTaskdocument,
)

COUNTRY_NAMES = {
    'IN': 'India',
}


def _get_country(code):
    if not code:
        return None
    return {
        'code': code,
        'name': COUNTRY_NAMES.get(code.upper()),
    }

PUBLISHED_REQUIRED_FIELDS = [
    'project_title', 'contract_type', 'project_value',
    'start_date', 'end_date', 'site_address_line_1',
    'site_city', 'site_state', 'site_zip_code',
]

STATUS_CHOICES = ['draft', 'pending', 'in_progress', 'completed']
OBLIGATION_STATUS_CHOICES = ['pending', 'in_progress', 'completed']


class ContractOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.CharField()
    organisation_id = serializers.IntegerField()
    law_firm_id = serializers.IntegerField()
    project_title = serializers.CharField()
    contract_type_id = serializers.IntegerField(allow_null=True)
    project_value = serializers.SerializerMethodField()
    start_date = serializers.DateField(allow_null=True)
    end_date = serializers.DateField(allow_null=True)
    counter_party = serializers.CharField(allow_null=True)
    site_address_line_1 = serializers.CharField(allow_null=True)
    site_address_line_2 = serializers.CharField(allow_null=True)
    site_city = serializers.CharField(allow_null=True)
    site_state = serializers.CharField(allow_null=True)
    site_zip_code = serializers.CharField(allow_null=True)
    site_country = serializers.SerializerMethodField()
    contract_parent_id = serializers.IntegerField(allow_null=True)
    created_at = serializers.DateTimeField()

    def get_project_value(self, obj):
        return str(obj.project_value) if obj.project_value else None

    def get_site_country(self, obj):
        return _get_country(obj.site_country)


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


class ContractTaskCreateSerializer(serializers.Serializer):
    task_title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    work_type = serializers.ChoiceField(choices=['own_work', 'vendor_work'])
    obligation_id = serializers.IntegerField()
    task_type_id = serializers.IntegerField()
    parent_task_id = serializers.IntegerField(required=False, allow_null=True)
    assigned_to_role_id = serializers.IntegerField(required=False, allow_null=True)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    task_status = serializers.ChoiceField(choices=['pending', 'in_progress', 'completed'])
    progress_percentage = serializers.IntegerField(required=False, min_value=0, max_value=100)

    def validate_obligation_id(self, value):
        contract = self.context.get('contract')
        if not ObligationsObligation.objects.filter(id=value, contract_id=contract.id, deleted_at__isnull=True).exists():
            raise serializers.ValidationError('Obligation not found for this contract.')
        return value

    def validate_task_type_id(self, value):
        if not MastersTasktype.objects.filter(id=value, deleted_at__isnull=True).exists():
            raise serializers.ValidationError('Task type not found.')
        return value

    def validate_parent_task_id(self, value):
        if value is None:
            return value

        task = TasksContracttask.objects.filter(id=value, deleted_at__isnull=True).first()
        if not task:
            raise serializers.ValidationError('Parent task not found.')

        obligation_id = self.initial_data.get('obligation_id')
        if task.obligation_id != obligation_id:
            raise serializers.ValidationError('Parent task must belong to the same obligation.')

        if task.parent_task_id:
            raise serializers.ValidationError('Parent task cannot be a subtask.')

        return value

    def validate_assigned_to_role_id(self, value):
        if value is None:
            return value
        if not MastersContractroletype.objects.filter(id=value).exists():
            raise serializers.ValidationError('Assigned role not found.')
        return value

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({'end_date': 'end_date must be after start_date.'})

        return data


class ContractTaskUpdateSerializer(serializers.Serializer):
    task_title = serializers.CharField(max_length=255, required=False, allow_blank=False)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    work_type = serializers.ChoiceField(choices=['own_work', 'vendor_work'], required=False)
    task_type_id = serializers.IntegerField(required=False)
    parent_task_id = serializers.IntegerField(required=False, allow_null=True)
    assigned_to_role_id = serializers.IntegerField(required=False, allow_null=True)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    task_status = serializers.ChoiceField(choices=['pending', 'in_progress', 'completed'], required=False)
    progress_percentage = serializers.IntegerField(required=False, min_value=0, max_value=100)
    comment = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_task_type_id(self, value):
        if not MastersTasktype.objects.filter(id=value, deleted_at__isnull=True).exists():
            raise serializers.ValidationError('Task type not found.')
        return value

    def validate_parent_task_id(self, value):
        if value is None:
            return value

        task = TasksContracttask.objects.filter(id=value, deleted_at__isnull=True).first()
        if not task:
            raise serializers.ValidationError('Parent task not found.')

        current_task = self.context.get('task')
        if task.obligation_id != current_task.obligation_id:
            raise serializers.ValidationError('Parent task must belong to the same obligation.')

        if task.parent_task_id:
            raise serializers.ValidationError('Parent task cannot be a subtask.')

        if current_task.id == task.id:
            raise serializers.ValidationError('Task cannot be its own parent.')

        return value

    def validate_assigned_to_role_id(self, value):
        if value is None:
            return value
        if not MastersContractroletype.objects.filter(id=value).exists():
            raise serializers.ValidationError('Assigned role not found.')
        return value

    def validate(self, data):
        task = self.context.get('task')
        start_date = data.get('start_date', task.start_date if task else None)
        end_date = data.get('end_date', task.end_date if task else None)

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({'end_date': 'end_date must be after start_date.'})

        return data


class TaskOutputSerializer(serializers.Serializer):
    include_subtasks = False

    def __init__(self, instance, many=False, include_subtasks=False, **kwargs):
        super().__init__(instance=instance, many=many, **kwargs)
        self.include_subtasks = include_subtasks

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'task_title': instance.task_title,
            'description': instance.description,
            'work_type': instance.work_type,
            'task_type': self._get_task_type_data(instance.task_type_id),
            'assigned_to_role': self._get_role_data(instance.assigned_to_role_id),
            'parent_task': self._get_parent_task_data(instance.parent_task_id),
            'obligation': self._get_obligation_data(instance.obligation_id),
            'start_date': instance.start_date,
            'end_date': instance.end_date,
            'task_status': instance.task_status,
            'progress_percentage': instance.progress_percentage,
            'subtasks_count': self._get_subtasks_count(instance.id),
            'documents_count': self._get_documents_count(instance.id),
            'subtasks': self._get_subtasks(instance.id) if self.include_subtasks else None,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at,
        }

    def _get_task_type_data(self, task_type_id):
        if not task_type_id:
            return None
        task_type = MastersTasktype.objects.filter(id=task_type_id).first()
        if not task_type:
            return None
        return {'id': task_type.id, 'name': task_type.name}

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

    def _get_parent_task_data(self, parent_task_id):
        if not parent_task_id:
            return None
        parent_task = TasksContracttask.objects.filter(id=parent_task_id, deleted_at__isnull=True).first()
        if not parent_task:
            return None
        return {
            'id': parent_task.id,
            'task_title': parent_task.task_title,
            'task_status': parent_task.task_status,
        }

    def _get_obligation_data(self, obligation_id):
        obligation = ObligationsObligation.objects.filter(id=obligation_id, deleted_at__isnull=True).first()
        if not obligation:
            return None
        return {
            'id': obligation.id,
            'obligation_title': obligation.obligation_title,
        }

    def _get_subtasks_count(self, task_id):
        return TasksContracttask.objects.filter(parent_task_id=task_id, deleted_at__isnull=True).count()

    def _get_documents_count(self, task_id):
        return TasksTaskdocument.objects.filter(task_id=task_id, deleted_at__isnull=True).count()

    def _get_subtasks(self, task_id):
        subtasks = TasksContracttask.objects.filter(parent_task_id=task_id, deleted_at__isnull=True).order_by('created_at')
        result = []
        for subtask in subtasks:
            result.append({
                'id': subtask.id,
                'task_title': subtask.task_title,
                'description': subtask.description,
                'work_type': subtask.work_type,
                'task_type': self._get_task_type_data(subtask.task_type_id),
                'assigned_to_role': self._get_role_data(subtask.assigned_to_role_id),
                'start_date': subtask.start_date,
                'end_date': subtask.end_date,
                'task_status': subtask.task_status,
                'progress_percentage': subtask.progress_percentage,
                'created_at': subtask.created_at,
            })
        return result


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

        return data
