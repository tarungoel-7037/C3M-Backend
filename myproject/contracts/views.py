import os
import uuid
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.utils.text import get_valid_filename
from rest_framework.pagination import PageNumberPagination

from accounts.models import LawFirm, Organisation, UserLawFirmAccess, UserOrganisationAccess
from contracts.serializers import (
    ContractCreateSerializer,
    ContractDocumentOutputSerializer,
    ContractDocumentUploadSerializer,
    ContractOutputSerializer,
    ContractTaskCreateSerializer,
    ContractTaskUpdateSerializer,
    ObligationCreateSerializer,
    ObligationOutputSerializer,
    ObligationUpdateSerializer,
    TaskOutputSerializer,
)
from myapp.models import (
    ContractsContract,
    ContractsContractdocument,
    ObligationsEscalationmatrix,
    ObligationsObligation,
    MastersContracttype,
    MastersDocumenttype,
    MastersTasktype,
    TasksContracttask,
    TasksTaskdocument,
    TasksTaskfieldchange,
    TasksTaskupdate,
)
from myproject.constants import (
    AuditAction,
    AuditModule,
    ErrorCode,
    ErrorMessage,
    SuccessCode,
    SuccessMessage,
)
from myproject.utils import ApiView, _error, _success, log_action


COUNTRY_NAMES = {
    'IN': 'India',
}


def _get_contract(contract_id):
    return ContractsContract.objects.filter(id=contract_id, deleted_at__isnull=True).first()


def _get_obligation(obligation_id):
    return ObligationsObligation.objects.filter(id=obligation_id, deleted_at__isnull=True).first()


def _get_country(code):
    if not code:
        return None
    return {
        'code': code,
        'name': COUNTRY_NAMES.get(code.upper()),
    }


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


class ContractsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100


def _save_contract_document_file(file_obj, contract_id):
    upload_dir = Path(settings.BASE_DIR) / 'uploads' / 'contracts' / str(contract_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    sanitized_name = get_valid_filename(file_obj.name)
    unique_name = f"{uuid.uuid4().hex}_{sanitized_name}"
    saved_path = upload_dir / unique_name

    with open(saved_path, 'wb+') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)

    return str(Path('uploads') / 'contracts' / str(contract_id) / unique_name).replace('\\', '/')


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

        log_action(
            request,
            action=AuditAction.CREATE_CONTRACT,
            module=AuditModule.CONTRACTS,
            obj_id=contract.id,
            action_details=f'Created contract {contract.project_title}',
            related_object_id=contract.id,
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

        contracts = contracts.order_by('-created_at')
        paginator = ContractsPagination()
        page = paginator.paginate_queryset(contracts, request)
        serializer = ContractOutputSerializer(page, many=True)

        return _success('Contracts retrieved successfully.', data={
            'contracts': serializer.data,
            'pagination': {
                'total': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
            },
        })


class ContractDocumentUploadView(ApiView):
    login_required = True

    def post(self, request, contract_id):
        contract = _get_contract(contract_id)
        if not contract:
            return _error(ErrorMessage.CONTRACT_NOT_FOUND, status=404)

        if not _user_has_contract_access(request.user, contract):
            return _error(ErrorMessage.CONTRACT_ACCESS_DENIED, status=403)

        serializer = ContractDocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return _error(
                ErrorMessage.VALIDATION_ERROR,
                message_code=ErrorCode.VALIDATION_ERROR,
                errors=serializer.errors,
            )

        vd = serializer.validated_data
        file_obj = vd['file']
        file_path = _save_contract_document_file(file_obj, contract.id)
        now = timezone.now()

        document = ContractsContractdocument.objects.create(
            document_name=file_obj.name,
            file_path=file_path,
            file_size=file_obj.size,
            file_type=file_obj.content_type,
            description=vd.get('description'),
            contract_id=contract.id,
            document_type_id=vd['document_type'],
            uploaded_by_id=request.user.id if request.user and request.user.is_authenticated else None,
            created_at=now,
            updated_at=now,
        )

        log_action(
            request,
            action=AuditAction.UPLOAD_CONTRACT_DOCUMENT,
            module=AuditModule.CONTRACT_DOCUMENTS,
            obj_id=document.id,
            action_details=f'Uploaded document {document.document_name} for contract {contract.project_title}',
            related_object_id=contract.id,
        )

        output = ContractDocumentOutputSerializer(document)
        return _success(
            'Contract document uploaded successfully.',
            message_code=SuccessCode.DEFAULT,
            data={'document': output.data},
            status=201,
        )


class ContractDocumentListView(ApiView):
    login_required = True

    def get(self, request, contract_id):
        contract = _get_contract(contract_id)
        if not contract:
            return _error(ErrorMessage.CONTRACT_NOT_FOUND, status=404)

        if not _user_has_contract_access(request.user, contract):
            return _error(ErrorMessage.CONTRACT_ACCESS_DENIED, status=403)

        signed = request.GET.get('signed', '').lower() == 'true'
        documents = ContractsContractdocument.objects.filter(
            contract_id=contract.id,
            deleted_at__isnull=True,
        )

        if signed:
            contract_document_type_ids = MastersDocumenttype.objects.filter(
                name__iexact='contract document'
            ).values_list('id', flat=True)
            documents = documents.filter(document_type_id__in=contract_document_type_ids)

        documents = documents.order_by('-created_at')
        serializer = ContractDocumentOutputSerializer(documents, many=True)

        return _success(
            'Contract documents retrieved successfully.',
            message_code=SuccessCode.DEFAULT,
            data={'documents': serializer.data},
        )


class ContractDocumentDetailView(ApiView):
    login_required = True

    def get(self, request, contract_id, document_id):
        contract = _get_contract(contract_id)
        if not contract:
            return _error(ErrorMessage.CONTRACT_NOT_FOUND, status=404)

        if not _user_has_contract_access(request.user, contract):
            return _error(ErrorMessage.CONTRACT_ACCESS_DENIED, status=403)

        document = ContractsContractdocument.objects.filter(
            id=document_id,
            contract_id=contract.id,
            deleted_at__isnull=True,
        ).first()

        if not document:
            return _error('Document not found.', status=404)

        serializer = ContractDocumentOutputSerializer(document)
        return _success(
            'Document retrieved successfully.',
            message_code=1206,
            data=serializer.data,
        )


class ContractDocumentDeleteView(ApiView):
    login_required = True

    def delete(self, request, contract_id, document_id):
        contract = _get_contract(contract_id)
        if not contract:
            return _error(ErrorMessage.CONTRACT_NOT_FOUND, status=404)

        if not _user_has_contract_access(request.user, contract):
            return _error(ErrorMessage.CONTRACT_ACCESS_DENIED, status=403)

        document = ContractsContractdocument.objects.filter(
            id=document_id,
            contract_id=contract.id,
            deleted_at__isnull=True,
        ).first()

        if not document:
            return _error('Document not found.', status=404)

        now = timezone.now()
        document.deleted_at = now
        document.updated_at = now
        document.save()

        log_action(
            request,
            action=AuditAction.DELETE_CONTRACT_DOCUMENT,
            module=AuditModule.CONTRACT_DOCUMENTS,
            obj_id=document.id,
            action_details=f'Deleted document {document.document_name} from contract {contract.project_title}',
            related_object_id=contract.id,
        )

        return _success(
            'Document deleted successfully.',
            message_code=1207,
            data={'id': document.id},
        )


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

        log_action(
            request,
            action=AuditAction.CREATE_OBLIGATION,
            module=AuditModule.OBLIGATIONS,
            obj_id=obligation.id,
            action_details=f'Created obligation {obligation.obligation_title} for contract {contract.project_title}',
            related_object_id=contract.id,
        )

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
        
        paginator = ContractsPagination()
        page = paginator.paginate_queryset(obligations, request)
        serializer = ObligationOutputSerializer(page, many=True)
        
        return _success(
            SuccessMessage.OBLIGATIONS_LISTED,
            message_code=SuccessCode.OBLIGATIONS_LISTED,
            data={
                'obligations': serializer.data,
                'pagination': {
                    'total': paginator.page.paginator.count,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                },
            },
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

        paginator = ContractsPagination()
        page = paginator.paginate_queryset(tasks, request)
        serializer = TaskOutputSerializer(page, many=True)
        
        return _success(
            SuccessMessage.TASKS_LISTED,
            message_code=SuccessCode.TASKS_LISTED,
            data={
                'tasks': serializer.data,
                'pagination': {
                    'total': paginator.page.paginator.count,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                },
            },
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

        obligation = _get_obligation(task.obligation_id)

        log_action(
            request,
            action=AuditAction.CREATE_CONTRACT_TASK,
            module=AuditModule.TASKS,
            obj_id=task.id,
            action_details=f'Created task {task.task_title} for obligation {obligation.obligation_title if obligation else task.obligation_id}',
            related_object_id=task.obligation_id,
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
        changed_fields_payload = {}
        old_task_status = task.task_status
        for input_key, model_field in field_map.items():
            if input_key in vd:
                old_value = getattr(task, model_field)
                new_value = vd[input_key]
                if old_value != new_value:
                    changed_fields.append((input_key, old_value, new_value))
                    changed_fields_payload[input_key] = {'old': old_value, 'new': new_value}
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

        log_action(
            request,
            action=AuditAction.UPDATE_CONTRACT_TASK,
            module=AuditModule.TASKS,
            obj_id=task.id,
            action_details=f'Updated task {task.task_title} for obligation {obligation.obligation_title}',
            related_object_id=obligation.id,
        )

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

        log_action(
            request,
            action=AuditAction.DELETE_CONTRACT_TASK,
            module=AuditModule.TASKS,
            obj_id=task.id,
            action_details=f'Deleted task {task.task_title} for obligation {obligation.obligation_title}',
            related_object_id=obligation.id,
        )

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

        changed_fields = {}
        from_status = ''
        to_status = ''

        with transaction.atomic():
            for input_key, model_field in updatable_fields.items():
                if input_key in vd:
                    old_value = getattr(obligation, model_field)
                    new_value = vd[input_key]
                    if old_value != new_value:
                        changed_fields[input_key] = {'old': old_value, 'new': new_value}
                        if input_key == 'status':
                            from_status = old_value or ''
                            to_status = new_value or ''
                    setattr(obligation, model_field, vd[input_key])

            obligation.updated_at = now
            obligation.save()

            if 'escalation_matrix' in vd:
                _sync_escalation_matrix(obligation, vd.get('escalation_matrix', []), now)

        log_action(
            request,
            action=AuditAction.UPDATE_OBLIGATION,
            module=AuditModule.OBLIGATIONS,
            obj_id=obligation.id,
            action_details=f'Updated obligation {obligation.obligation_title} for contract {contract.project_title}',
            related_object_id=contract.id,
        )

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

        log_action(
            request,
            action=AuditAction.DELETE_OBLIGATION,
            module=AuditModule.OBLIGATIONS,
            obj_id=obligation.id,
            action_details=f'Deleted obligation {obligation.obligation_title} from contract {contract.project_title}',
            related_object_id=contract.id,
        )

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

        organisation = Organisation.objects.filter(id=contract.organisation_id).first()
        law_firm = LawFirm.objects.filter(id=contract.law_firm_id).first()
        created_by = User.objects.filter(id=contract.created_by_id).first()
        contract_type = None
        if contract.contract_type_id:
            contract_type = MastersContracttype.objects.filter(id=contract.contract_type_id, deleted_at__isnull=True).first()
            if contract_type:
                contract_type = {
                    'id': contract_type.id,
                    'name': contract_type.name,
                }

        data = {
            'id': contract.id,
            'project_title': contract.project_title,
            'counter_party': contract.counter_party,
            'project_value': str(contract.project_value) if contract.project_value else None,
            'start_date': contract.start_date,
            'end_date': contract.end_date,
            'status': contract.status,
            'organisation': {
                'id': organisation.id if organisation else None,
                'name': organisation.name if organisation else None,
                'entity_type': 'organisation',
            } if organisation else None,
            'law_firm': {
                'id': law_firm.id if law_firm else None,
                'name': law_firm.name if law_firm else None,
                'entity_type': 'law_firm',
            } if law_firm else None,
            'contract_type': contract_type,
            'created_by': {
                'id': created_by.id,
                'full_name': ' '.join(filter(None, [created_by.first_name, created_by.last_name])) or created_by.username,
                'email': created_by.email,
            } if created_by else None,
            'site_address_line_1': contract.site_address_line_1,
            'site_address_line_2': contract.site_address_line_2,
            'site_city': contract.site_city,
            'site_state': contract.site_state,
            'site_zip_code': contract.site_zip_code,
            'site_country': _get_country(contract.site_country),
            'created_at': contract.created_at,
            'updated_at': contract.updated_at,
        }
        return _success(
            SuccessMessage.CONTRACT_RETRIEVED,
            message_code=SuccessCode.CONTRACT_RETRIEVED,
            data=data,
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

        log_action(
            request,
            action=AuditAction.DELETE_CONTRACT,
            module=AuditModule.CONTRACTS,
            obj_id=contract.id,
            action_details=f'Deleted contract {contract.project_title}',
            related_object_id=contract.id,
        )

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