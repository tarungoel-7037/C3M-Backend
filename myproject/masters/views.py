from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

from accounts.models import GroupProfile
from myapp.models import MastersContractroletype, MastersContracttype, MastersTasktype
from myproject.constants import SuccessCode, SuccessMessage
from myproject.utils import ApiView, _success


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
        fields = ['id', 'role_name', 'description', 'created_at']


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
        serializer = ContractTypeSerializer(contract_types, many=True)

        return _success(
            SuccessMessage.CONTRACT_TYPES_RETRIEVED,
            message_code=SuccessCode.CONTRACT_TYPES_RETRIEVED,
            data={
                'contract_types': serializer.data,
                'pagination': {
                    'total': contract_types.count(),
                    'next': None,
                    'previous': None,
                },
            },
        )


class ContractTaskTypeListView(ApiView):
    def get(self, request):
        task_types = MastersTasktype.objects.filter(deleted_at__isnull=True).order_by('-created_at')
        serializer = TaskTypeSerializer(task_types, many=True)

        return _success(
            SuccessMessage.TASK_TYPES_RETRIEVED,
            message_code=SuccessCode.TASK_TYPES_RETRIEVED,
            data={
                'task_types': serializer.data,
                'pagination': {
                    'total': task_types.count(),
                    'next': None,
                    'previous': None,
                },
            },
        )


class ContractRoleTypeListView(ApiView):
    def get(self, request):
        contract_role_types = MastersContractroletype.objects.filter(deleted_at__isnull=True).order_by('-created_at')
        serializer = ContractRoleTypeSerializer(contract_role_types, many=True)

        return _success(
            SuccessMessage.CONTRACT_ROLE_TYPES_RETRIEVED,
            message_code=SuccessCode.CONTRACT_ROLE_TYPES_RETRIEVED,
            data={
                'contract_role_types': serializer.data,
                'pagination': {
                    'total': contract_role_types.count(),
                    'next': None,
                    'previous': None,
                },
            },
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
