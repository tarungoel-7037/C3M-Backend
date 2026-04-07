from rest_framework import serializers

from accounts.models import LawFirm, Organisation
from myapp.models import ContractsContract, MastersContracttype

PUBLISHED_REQUIRED_FIELDS = [
    'project_title', 'contract_type', 'project_value',
    'start_date', 'end_date', 'site_address_line_1',
    'site_city', 'site_state', 'site_zip_code',
]

STATUS_CHOICES = ['draft', 'pending', 'in_progress', 'completed']


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
