from django.db import transaction
from django.utils import timezone

from accounts.models import UserLawFirmAccess, UserOrganisationAccess
from contracts.serializers import (
    ContractCreateSerializer,
    ContractTaskCreateSerializer,
    ContractTaskUpdateSerializer,
    ObligationCreateSerializer,
    ObligationOutputSerializer,
    ObligationUpdateSerializer,
    TaskOutputSerializer,
)
from myapp.models import (
    ContractsContract,
    ObligationsEscalationmatrix,
    ObligationsObligation,
    MastersTasktype,
    TasksContracttask,
    TasksTaskdocument,
    TasksTaskfieldchange,
    TasksTaskupdate,
)
from myproject.constants import ErrorCode, ErrorMessage, SuccessCode, SuccessMessage
from myproject.utils import ApiView, _error, _success


def _get_contract(contract_id):
    return ContractsContract.objects.filter(id=contract_id, deleted_at__isnull=True).first()


def _get_obligation(obligation_id):
    return ObligationsObligation.objects.filter(id=obligation_id, deleted_at__isnull=True).first()


def _get_task(task_id):
    return TasksContracttask.objects.filter(id=task_id, deleted_at__isnull=True).first()


def _user_has_contract_access(user, contract):
    if not user or not user.is_authenticated or not contract:
        return False

    has_law_firm_access = UserLawFirmAccess.objects.filter(
        user_id=user.id,
        law_firm_id=contract.law_firm_id,
    ).exists()
    has_organisation_access = UserOrganisationAccess.objects.filter(
        user_id=user.id,
        organisation_id=contract.organisation_id,
    ).exists()
    return has_law_firm_access or has_organisation_access


def _sync_escalation_matrix(obligation, escalation_matrix, now):
    ObligationsEscalationmatrix.objects.filter(
        obligation_id=obligation.id,
        deleted_at__isnull=True,
    ).update(deleted_at=now, updated_at=now)

    if not escalation_matrix:
        return

    escalations = [
        ObligationsEscalationmatrix(
            obligation_id=obligation.id,
            level=item['level'],
            days=item['days'],
            notify_role_id=item['role_id'],
            is_triggered=False,
            triggered_at=None,
            created_at=now,
            updated_at=now,
        )
        for item in escalation_matrix
    ]
    ObligationsEscalationmatrix.objects.bulk_create(escalations)


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
        group_ids = set(request.user.groups.values_list('id', flat=True))

        if group_ids.intersection({1, 2}):
            organisation_ids = list(
                UserOrganisationAccess.objects.filter(user_id=request.user.id)
                .values_list('organisation_id', flat=True)
            )
            if not organisation_ids:
                return _success('Contracts retrieved successfully.', data={'contracts': []})

            contracts = ContractsContract.objects.filter(organisation_id__in=organisation_ids,deleted_at__isnull=True)
        else:
            law_firm_ids = list(
                UserLawFirmAccess.objects.filter(user_id=request.user.id)
                .values_list('law_firm_id', flat=True)
            )
            if not law_firm_ids:
                return _success('Contracts retrieved successfully.', data={'contracts': []})

            contracts = ContractsContract.objects.filter(law_firm_id__in=law_firm_ids,deleted_at__isnull=True)

        if not contracts:
            return _success('Contracts retrieved successfully.', data={'contracts': []})
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


class ObligationCreateView(ApiView):
    login_required = True

    def post(self, request, contract_id):
        contract = _get_contract(contract_id)
        if not contract:
            return _error(ErrorMessage.CONTRACT_NOT_FOUND, status=404)

        if not _user_has_contract_access(request.user, contract):
            return _error(ErrorMessage.CONTRACT_ACCESS_DENIED, status=403)

        data = request.data.get('data', request.data)
        serializer = ObligationCreateSerializer(data=data, context={'contract_id': contract.id})
        if not serializer.is_valid():
            return _error(
                ErrorMessage.VALIDATION_ERROR,
                message_code=ErrorCode.VALIDATION_ERROR,
                errors=serializer.errors,
            )

        vd = serializer.validated_data
        now = timezone.now()

        with transaction.atomic():
            obligation = ObligationsObligation.objects.create(
                obligation_title=vd['obligation_title'],
                description=vd.get('description'),
                page_section_reference=vd.get('page_section_reference'),
                extend_timeline_approval=vd.get('extend_timeline_approval'),
                obligation_type=vd['obligation_type'],
                party_type=vd.get('party_type', 'organisation'),
                start_date=vd.get('start_date'),
                end_date=vd.get('end_date'),
                status=vd.get('status', 'pending'),
                progress_percentage=0,
                assigned_role_id=vd['assigned_role'],
                contract_id=contract.id,
                obligation_document_id=vd.get('obligation_document'),
                created_at=now,
                updated_at=now,
            )
            _sync_escalation_matrix(obligation, vd.get('escalation_matrix', []), now)

        output = ObligationOutputSerializer(obligation)
        return _success(
            SuccessMessage.OBLIGATION_CREATED,
            message_code=SuccessCode.OBLIGATION_CREATED,
            data={'obligation': output.data},
            status=201,
        )


class ObligationListView(ApiView):
    login_required = True

    def get(self, request, contract_id):
        contract = _get_contract(contract_id)
        if not contract:
            return _error(ErrorMessage.CONTRACT_NOT_FOUND, status=404)

        if not _user_has_contract_access(request.user, contract):
            return _error(ErrorMessage.CONTRACT_ACCESS_DENIED, status=403)

        obligations = ObligationsObligation.objects.filter(
            contract_id=contract.id,
            deleted_at__isnull=True,
        ).order_by('-created_at')
        serializer = ObligationOutputSerializer(obligations, many=True)
        return _success(
            SuccessMessage.OBLIGATIONS_LISTED,
            message_code=SuccessCode.OBLIGATIONS_LISTED,
            data={'obligations': serializer.data},
        )


class ContractTaskListView(ApiView):
    login_required = True

    def get(self, request, contract_id):
        contract = _get_contract(contract_id)
        if not contract:
            return _error(ErrorMessage.CONTRACT_NOT_FOUND, status=404)

        if not _user_has_contract_access(request.user, contract):
            return _error(ErrorMessage.CONTRACT_ACCESS_DENIED, status=403)

        obligation_ids = ObligationsObligation.objects.filter(
            contract_id=contract.id,
            deleted_at__isnull=True,
        ).values_list('id', flat=True)

        tasks = TasksContracttask.objects.filter(
            obligation_id__in=obligation_ids,
            deleted_at__isnull=True,
        ).order_by('-created_at')

        serializer = TaskOutputSerializer(tasks, many=True)
        return _success(
            SuccessMessage.TASKS_LISTED,
            message_code=SuccessCode.TASKS_LISTED,
            data={'tasks': serializer.data},
        )


class ContractTaskCreateView(ApiView):
    login_required = True

    def post(self, request, contract_id):
        contract = _get_contract(contract_id)
        if not contract:
            return _error(ErrorMessage.CONTRACT_NOT_FOUND, status=404)

        if not _user_has_contract_access(request.user, contract):
            return _error(ErrorMessage.CONTRACT_ACCESS_DENIED, status=403)

        data = request.data.get('data', request.data)
        serializer = ContractTaskCreateSerializer(data=data, context={'contract': contract})
        if not serializer.is_valid():
            return _error(
                ErrorMessage.VALIDATION_ERROR,
                message_code=ErrorCode.VALIDATION_ERROR,
                errors=serializer.errors,
            )

        vd = serializer.validated_data
        now = timezone.now()

        task = TasksContracttask.objects.create(
            task_title=vd['task_title'],
            description=vd.get('description'),
            work_type=vd['work_type'],
            start_date=vd['start_date'],
            end_date=vd['end_date'],
            task_status=vd['task_status'],
            progress_percentage=vd.get('progress_percentage', 0),
            assigned_to_role_id=vd.get('assigned_to_role_id'),
            obligation_id=vd['obligation_id'],
            parent_task_id=vd.get('parent_task_id'),
            task_type_id=vd['task_type_id'],
            created_at=now,
            updated_at=now,
        )

        output = TaskOutputSerializer(task)
        return _success(
            SuccessMessage.TASK_CREATED,
            message_code=SuccessCode.TASK_CREATED,
            data={'task': output.data},
            status=201,
        )


class TaskDetailView(ApiView):
    login_required = True

    def get(self, request, task_id):
        task = _get_task(task_id)
        if not task:
            return _error(ErrorMessage.TASK_NOT_FOUND, status=404)

        obligation = _get_obligation(task.obligation_id)
        if not obligation:
            return _error(ErrorMessage.OBLIGATION_NOT_FOUND, status=404)

        contract = _get_contract(obligation.contract_id)
        if not contract:
            return _error(ErrorMessage.CONTRACT_NOT_FOUND, status=404)

        if not _user_has_contract_access(request.user, contract):
            return _error(ErrorMessage.TASK_ACCESS_DENIED, status=403)

        serializer = TaskOutputSerializer(task, include_subtasks=True)
        return _success(
            SuccessMessage.TASK_RETRIEVED,
            message_code=SuccessCode.TASK_RETRIEVED,
            data=serializer.data,
        )


class TaskUpdateView(ApiView):
    login_required = True

    def patch(self, request, task_id):
        task = _get_task(task_id)
        if not task:
            return _error(ErrorMessage.TASK_NOT_FOUND, status=404)

        obligation = _get_obligation(task.obligation_id)
        if not obligation:
            return _error(ErrorMessage.OBLIGATION_NOT_FOUND, status=404)

        contract = _get_contract(obligation.contract_id)
        if not contract:
            return _error(ErrorMessage.CONTRACT_NOT_FOUND, status=404)

        if not _user_has_contract_access(request.user, contract):
            return _error(ErrorMessage.TASK_ACCESS_DENIED, status=403)

        data = request.data.get('data', request.data)
        serializer = ContractTaskUpdateSerializer(data=data, partial=True, context={'task': task})
        if not serializer.is_valid():
            return _error(
                ErrorMessage.VALIDATION_ERROR,
                message_code=ErrorCode.VALIDATION_ERROR,
                errors=serializer.errors,
            )

        vd = serializer.validated_data
        now = timezone.now()
        field_map = {
            'task_title': 'task_title',
            'description': 'description',
            'work_type': 'work_type',
            'task_type_id': 'task_type_id',
            'parent_task_id': 'parent_task_id',
            'assigned_to_role_id': 'assigned_to_role_id',
            'start_date': 'start_date',
            'end_date': 'end_date',
            'task_status': 'task_status',
            'progress_percentage': 'progress_percentage',
        }

        changed_fields = []
        for input_key, model_field in field_map.items():
            if input_key in vd:
                old_value = getattr(task, model_field)
                new_value = vd[input_key]
                if old_value != new_value:
                    changed_fields.append((input_key, old_value, new_value))
                setattr(task, model_field, new_value)

        task.updated_at = now
        task.save()

        if 'comment' in vd and vd.get('comment') is not None:
            task_update = TasksTaskupdate.objects.create(
                update_date=now.date(),
                comment_text=vd.get('comment'),
                is_issue=False,
                is_resolved=False,
                task_id=task.id,
                user_id=request.user.id if request.user and request.user.is_authenticated else None,
                created_at=now,
                updated_at=now,
            )

            field_change_records = []
            for field_name, old_value, new_value in changed_fields:
                field_change_records.append(TasksTaskfieldchange(
                    field_name=field_name,
                    old_value=str(old_value) if old_value is not None else None,
                    new_value=str(new_value) if new_value is not None else None,
                    task_update_id=task_update.id,
                    created_at=now,
                    updated_at=now,
                ))
            if field_change_records:
                TasksTaskfieldchange.objects.bulk_create(field_change_records)

        serializer = TaskOutputSerializer(task, include_subtasks=True)
        return _success(
            SuccessMessage.TASK_UPDATED,
            message_code=SuccessCode.TASK_UPDATED,
            data={'task': serializer.data},
        )


class TaskDeleteView(ApiView):
    login_required = True

    def delete(self, request, task_id):
        task = _get_task(task_id)
        if not task:
            return _error(ErrorMessage.TASK_NOT_FOUND, status=404)

        obligation = _get_obligation(task.obligation_id)
        if not obligation:
            return _error(ErrorMessage.OBLIGATION_NOT_FOUND, status=404)

        contract = _get_contract(obligation.contract_id)
        if not contract:
            return _error(ErrorMessage.CONTRACT_NOT_FOUND, status=404)

        if not _user_has_contract_access(request.user, contract):
            return _error(ErrorMessage.TASK_ACCESS_DENIED, status=403)

        now = timezone.now()
        task.deleted_at = now
        task.updated_at = now
        task.save()

        return _success(
            SuccessMessage.TASK_DELETED,
            message_code=SuccessCode.TASK_DELETED,
        )


class ObligationDetailView(ApiView):
    login_required = True

    def get(self, request, obligation_id):
        obligation = _get_obligation(obligation_id)
        if not obligation:
            return _error(ErrorMessage.OBLIGATION_NOT_FOUND, status=404)

        contract = _get_contract(obligation.contract_id)
        if not contract:
            return _error(ErrorMessage.CONTRACT_NOT_FOUND, status=404)

        if not _user_has_contract_access(request.user, contract):
            return _error(ErrorMessage.OBLIGATION_ACCESS_DENIED, status=403)

        serializer = ObligationOutputSerializer(obligation)
        return _success(
            SuccessMessage.OBLIGATION_RETRIEVED,
            message_code=SuccessCode.OBLIGATION_RETRIEVED,
            data={'obligation': serializer.data},
        )


class ObligationUpdateView(ApiView):
    login_required = True

    def patch(self, request, obligation_id):
        obligation = _get_obligation(obligation_id)
        if not obligation:
            return _error(ErrorMessage.OBLIGATION_NOT_FOUND, status=404)

        contract = _get_contract(obligation.contract_id)
        if not contract:
            return _error(ErrorMessage.CONTRACT_NOT_FOUND, status=404)

        if not _user_has_contract_access(request.user, contract):
            return _error(ErrorMessage.OBLIGATION_ACCESS_DENIED, status=403)

        data = request.data.get('data', request.data)
        serializer = ObligationUpdateSerializer(
            data=data,
            partial=True,
            context={'contract_id': contract.id, 'instance': obligation},
        )
        if not serializer.is_valid():
            return _error(
                ErrorMessage.VALIDATION_ERROR,
                message_code=ErrorCode.VALIDATION_ERROR,
                errors=serializer.errors,
            )

        vd = serializer.validated_data
        now = timezone.now()

        updatable_fields = {
            'obligation_title': 'obligation_title',
            'description': 'description',
            'page_section_reference': 'page_section_reference',
            'extend_timeline_approval': 'extend_timeline_approval',
            'obligation_type': 'obligation_type',
            'party_type': 'party_type',
            'start_date': 'start_date',
            'end_date': 'end_date',
            'status': 'status',
            'obligation_document': 'obligation_document_id',
            'assigned_role': 'assigned_role_id',
        }

        with transaction.atomic():
            for input_key, model_field in updatable_fields.items():
                if input_key in vd:
                    setattr(obligation, model_field, vd[input_key])

            obligation.updated_at = now
            obligation.save()

            if 'escalation_matrix' in vd:
                _sync_escalation_matrix(obligation, vd.get('escalation_matrix', []), now)

        output = ObligationOutputSerializer(obligation)
        return _success(
            SuccessMessage.OBLIGATION_UPDATED,
            message_code=SuccessCode.OBLIGATION_UPDATED,
            data={'obligation': output.data},
        )


class ObligationDeleteView(ApiView):
    login_required = True

    def delete(self, request, obligation_id):
        obligation = _get_obligation(obligation_id)
        if not obligation:
            return _error(ErrorMessage.OBLIGATION_NOT_FOUND, status=404)

        contract = _get_contract(obligation.contract_id)
        if not contract:
            return _error(ErrorMessage.CONTRACT_NOT_FOUND, status=404)

        if not _user_has_contract_access(request.user, contract):
            return _error(ErrorMessage.OBLIGATION_ACCESS_DENIED, status=403)

        now = timezone.now()
        with transaction.atomic():
            obligation.deleted_at = now
            obligation.updated_at = now
            obligation.save()
            ObligationsEscalationmatrix.objects.filter(
                obligation_id=obligation.id,
                deleted_at__isnull=True,
            ).update(deleted_at=now, updated_at=now)

        return _success(
            SuccessMessage.OBLIGATION_DELETED,
            message_code=SuccessCode.OBLIGATION_DELETED,
        )
        
        
class ContractDetailView(ApiView):
    login_required = True

    def get(self, request, contract_id):
        contract = _get_contract(contract_id)
        if not contract:
            return _error(ErrorMessage.CONTRACT_NOT_FOUND, status=404)

        if not _user_has_contract_access(request.user, contract):
            return _error(ErrorMessage.CONTRACT_ACCESS_DENIED, status=403)

        data = {
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
        return _success(
            SuccessMessage.CONTRACT_RETRIEVED,
            message_code=SuccessCode.CONTRACT_RETRIEVED,
            data={'contract': data},
        )


class ContractDeleteView(ApiView):
    login_required = True

    def delete(self, request, contract_id):
        contract = _get_contract(contract_id)
        if not contract:
            return _error(ErrorMessage.CONTRACT_NOT_FOUND, status=404)

        if not _user_has_contract_access(request.user, contract):
            return _error(ErrorMessage.CONTRACT_ACCESS_DENIED, status=403)

        now = timezone.now()
        with transaction.atomic():
            contract.deleted_at = now
            contract.updated_at = now
            contract.save()

            ContractsContract.objects.filter(
                id=contract.id,
                deleted_at__isnull=True,
            ).update(deleted_at=now, updated_at=now)

        return _success(
            SuccessMessage.CONTRACT_DELETED,
            message_code=SuccessCode.CONTRACT_DELETED,
        )
        
class ContractUpdateView(ApiView):
    login_required = True

    def patch(self, request, contract_id):
        contract = _get_contract(contract_id)
        if not contract:
            return _error(ErrorMessage.CONTRACT_NOT_FOUND, status=404)

        if not _user_has_contract_access(request.user, contract):
            return _error(ErrorMessage.CONTRACT_ACCESS_DENIED, status=403)

        data = request.data.get('data', request.data)
        serializer = ContractCreateSerializer(data=data, partial=True)
        if not serializer.is_valid():
            return _error(
                ErrorMessage.VALIDATION_ERROR,
                message_code=ErrorCode.VALIDATION_ERROR,
                errors=serializer.errors,
            )

        vd = serializer.validated_data
        now = timezone.now()

        updatable_fields = {
            'status': 'status',
            'project_title': 'project_title',
            'contract_type': 'contract_type_id',
            'project_value': 'project_value',
            'start_date': 'start_date',
            'end_date': 'end_date',
            'counter_party': 'counter_party',
            'site_address_line_1': 'site_address_line_1',
            'site_address_line_2': 'site_address_line_2',
            'site_city': 'site_city',
            'site_state': 'site_state',
            'site_zip_code': 'site_zip_code',
            'site_country': 'site_country',
            'contract_parent_id': 'contract_parent_id',
        }

        for input_key, model_field in updatable_fields.items():
            if input_key in vd:
                setattr(contract, model_field, vd[input_key])

        contract.updated_at = now
        contract.save()

        data = {
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
            'updated_at': contract.updated_at,
        }
        return _success(
            SuccessMessage.CONTRACT_UPDATED,
            message_code=SuccessCode.CONTRACT_UPDATED,
            data={'contract': data},
        )