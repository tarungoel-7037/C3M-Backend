from django.utils.timezone import now

from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

from accounts.models import GroupProfile
from myapp.models import (
    MastersContractpermission,
    MastersContractroletype,
    MastersContractroletypePermissions,
    MastersContracttype,
    MastersTasktype,
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


class ContractTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MastersContracttype
        fields = ['id', 'name', 'description', 'created_at']


class TaskTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MastersTasktype
        fields = ['id', 'name', 'description', 'created_at']


class ContractRoleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MastersContractroletype
        fields = ['id', 'role_name', 'display_name', 'description', 'group_entity_type', 'created_at']


class ContractRoleCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    display_name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, default='')
    group_entity_type = serializers.ChoiceField(
        choices=['law', 'org'],
        required=False,
        allow_blank=True,
        default='',
    )
    permissions = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
    )


class GroupSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='group.id')
    name = serializers.CharField(source='group.name')
    display_name = serializers.CharField()
    group_entity_type = serializers.CharField()


class MastersPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100


class ContractTypeListView(ApiView):
    def get(self, request):
        contract_types = MastersContracttype.objects.filter(deleted_at__isnull=True).order_by('-created_at')
        paginator = MastersPagination()
        page = paginator.paginate_queryset(contract_types, request)
        serializer = ContractTypeSerializer(page, many=True)

        return _success(
            SuccessMessage.CONTRACT_TYPES_RETRIEVED,
            message_code=SuccessCode.CONTRACT_TYPES_RETRIEVED,
            data={
                'contract_types': serializer.data,
                'pagination': {
                    'total': paginator.page.paginator.count,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                },
            },
        )


class ContractTaskTypeListView(ApiView):
    def get(self, request):
        task_types = MastersTasktype.objects.filter(deleted_at__isnull=True).order_by('-created_at')
        paginator = MastersPagination()
        page = paginator.paginate_queryset(task_types, request)
        serializer = TaskTypeSerializer(page, many=True)

        return _success(
            SuccessMessage.TASK_TYPES_RETRIEVED,
            message_code=SuccessCode.TASK_TYPES_RETRIEVED,
            data={
                'task_types': serializer.data,
                'pagination': {
                    'total': paginator.page.paginator.count,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                },
            },
        )


class ContractRoleTypeListView(ApiView):
    def get(self, request):
        contract_role_types = MastersContractroletype.objects.filter(deleted_at__isnull=True).order_by('-created_at')
        paginator = MastersPagination()
        page = paginator.paginate_queryset(contract_role_types, request)
        serializer = ContractRoleTypeSerializer(page, many=True)

        return _success(
            SuccessMessage.CONTRACT_ROLE_TYPES_RETRIEVED,
            message_code=SuccessCode.CONTRACT_ROLE_TYPES_RETRIEVED,
            data={
                'contract_role_types': serializer.data,
                'pagination': {
                    'total': paginator.page.paginator.count,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                },
            },
        )


class ContractRoleCreateView(ApiView):
    login_required = True

    def post(self, request):
        data = request.data.get('data', request.data)
        serializer = ContractRoleCreateSerializer(data=data)
        if not serializer.is_valid():
            return _error(
                ErrorMessage.VALIDATION_ERROR,
                message_code=ErrorCode.VALIDATION_ERROR,
                errors=serializer.errors,
            )

        vd = serializer.validated_data
        permission_names = vd.get('permissions', [])

        # Resolve permissions by name
        permissions = []
        if permission_names:
            permissions = list(
                MastersContractpermission.objects.filter(
                    name__in=permission_names,
                    deleted_at__isnull=True,
                )
            )
            found_names = {p.name for p in permissions}
            missing = set(permission_names) - found_names
            if missing:
                return _error(
                    ErrorMessage.PERMISSION_NOT_FOUND.format(names=', '.join(sorted(missing))),
                    message_code=ErrorCode.PERMISSION_NOT_FOUND,
                )

        ts = now()
        role = MastersContractroletype.objects.create(
            role_name=vd['name'],
            display_name=vd['display_name'],
            description=vd.get('description', ''),
            group_entity_type=vd.get('group_entity_type', '') or None,
            created_at=ts,
            updated_at=ts,
        )

        if permissions:
            MastersContractroletypePermissions.objects.bulk_create([
                MastersContractroletypePermissions(
                    contractroletype_id=role.id,
                    contractpermission_id=p.id,
                )
                for p in permissions
            ])

        log_action(
            request,
            action=AuditAction.CREATE_CONTRACT_ROLE,
            module=AuditModule.MASTERS,
            obj_id=role.id,
            action_details=f'Created contract role {role.role_name}',
        )

        return _success(
            SuccessMessage.CONTRACT_ROLE_CREATED,
            message_code=SuccessCode.CONTRACT_ROLE_CREATED,
            data={
                'role': {
                    'id': role.id,
                    'name': role.role_name,
                    'display_name': role.display_name,
                    'description': role.description,
                    'group_entity_type': role.group_entity_type,
                    'permissions': [
                        {'id': p.id, 'name': p.name, 'description': p.description}
                        for p in permissions
                    ],
                    'created_at': role.created_at,
                }
            },
            status=201,
        )


class GroupListView(ApiView):
    def get(self, request):
        groups = GroupProfile.objects.select_related('group').all().order_by('group__name')
        paginator = MastersPagination()
        page = paginator.paginate_queryset(groups, request)
        serializer = GroupSerializer(page, many=True)

        return _success(
            SuccessMessage.GROUPS_RETRIEVED,
            message_code=SuccessCode.GROUPS_RETRIEVED,
            data={
                'groups': serializer.data,
                'pagination': {
                    'total': paginator.page.paginator.count,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                },
            },
        )
        
        
class DocumentDownloadView(ApiView):
    def post(self, request):
        pass