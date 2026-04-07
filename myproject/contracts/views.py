from django.utils import timezone

from accounts.models import UserOrganisationAccess
from contracts.serializers import ContractCreateSerializer
from myapp.models import ContractsContract
from myproject.constants import ErrorCode, ErrorMessage, SuccessCode, SuccessMessage
from myproject.utils import ApiView, _error, _success


class ContractCreateView(ApiView):
    login_required = True

    def post(self, request):
        data = request.data.get('data', request.data)
        serializer = ContractCreateSerializer(data=data)
        if not serializer.is_valid():
            return _error(
                ErrorMessage.VALIDATION_ERROR,
                message_code=ErrorCode.VALIDATION_ERROR,
                errors=serializer.errors,
            )

        vd = serializer.validated_data
        now = timezone.now()

        contract = ContractsContract.objects.create(
            organisation_id=vd['organisation'],
            law_firm_id=vd['law_firm'],
            status=vd.get('status', 'draft'),
            project_title=vd.get('project_title'),
            contract_type_id=vd.get('contract_type'),
            project_value=vd.get('project_value'),
            start_date=vd.get('start_date'),
            end_date=vd.get('end_date'),
            site_address_line_1=vd.get('site_address_line_1'),
            site_address_line_2=vd.get('site_address_line_2'),
            site_city=vd.get('site_city'),
            site_state=vd.get('site_state'),
            site_zip_code=vd.get('site_zip_code'),
            site_country=vd.get('site_country'),
            counter_party=vd.get('counter_party'),
            contract_parent_id=vd.get('contract_parent_id'),
            created_by_id=request.user.id if request.user and request.user.is_authenticated else None,
            is_open_ended=False,
            created_at=now,
            updated_at=now,
        )

        return _success(
            SuccessMessage.CONTRACT_CREATED,
            message_code=SuccessCode.CONTRACT_CREATED,
            data={
                'contract': {
                    'id': contract.id,
                    'status': contract.status,
                    'organisation_id': contract.organisation_id,
                    'law_firm_id': contract.law_firm_id,
                    'project_title': contract.project_title,
                    'contract_type_id': contract.contract_type_id,
                    'project_value': str(contract.project_value) if contract.project_value else None,
                    'start_date': contract.start_date,
                    'end_date': contract.end_date,
                    'counter_party': contract.counter_party,
                    'site_address_line_1': contract.site_address_line_1,
                    'site_address_line_2': contract.site_address_line_2,
                    'site_city': contract.site_city,
                    'site_state': contract.site_state,
                    'site_zip_code': contract.site_zip_code,
                    'site_country': contract.site_country,
                    'contract_parent_id': contract.contract_parent_id,
                    'created_at': contract.created_at,
                }
            },
            status=201,
        )


class ContractListView(ApiView):
    login_required = True
    
    def get(self, request):
        access = UserOrganisationAccess.objects.filter(user_id=request.user.id).first()
        if not access:
            return _success('Contracts retrieved successfully.', data={'contracts': []})

        contracts = ContractsContract.objects.filter(organisation_id=access.organisation_id)
        data = []
        for contract in contracts:
            data.append({
                'id': contract.id,
                'status': contract.status,
                'organisation_id': contract.organisation_id,
                'law_firm_id': contract.law_firm_id,
                'project_title': contract.project_title,
                'contract_type_id': contract.contract_type_id,
                'project_value': str(contract.project_value) if contract.project_value else None,
                'start_date': contract.start_date,
                'end_date': contract.end_date,
                'counter_party': contract.counter_party,
                'site_address_line_1': contract.site_address_line_1,
                'site_address_line_2': contract.site_address_line_2,
                'site_city': contract.site_city,
                'site_state': contract.site_state,
                'site_zip_code': contract.site_zip_code,
                'site_country': contract.site_country,
                'contract_parent_id': contract.contract_parent_id,
                'created_at': contract.created_at,
            })
        return _success('Contracts retrieved successfully.', data={'contracts': data})
    