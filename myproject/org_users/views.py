from django.contrib.auth.models import Group, User
from rest_framework.pagination import PageNumberPagination

from accounts.models import Organisation, UserOrganisationAccess, UserProfile
from myproject.constants import ErrorCode, ErrorMessage, SuccessCode, SuccessMessage
from myproject.utils import ApiView, _error, _success
from org_users.serializers import (
    AddOrganisationUserSerializer,
    OrganisationUserSerializer,
    UpdateOrganisationUserSerializer,
)


class OrganisationUserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100


class OrganisationUsersView(ApiView):
    login_required = True

    def get(self, request, organisation_id):
        try:
            organisation = Organisation.objects.get(id=organisation_id)
        except Organisation.DoesNotExist:
            return _error(ErrorMessage.ORGANISATION_NOT_FOUND, message_code=ErrorCode.ORGANISATION_NOT_FOUND, status=404)

        user_ids = UserOrganisationAccess.objects.filter(
            organisation=organisation
        ).values_list('user_id', flat=True)

        users = User.objects.filter(id__in=user_ids).select_related('profile').prefetch_related(
            'law_firm_accesses__law_firm',
            'law_firm_accesses__group',
            'organisation_accesses__organisation__law_firm',
        ).order_by('-profile__created_at')

        paginator = OrganisationUserPagination()
        page = paginator.paginate_queryset(users, request)
        serializer = OrganisationUserSerializer(page, many=True)

        return _success(SuccessMessage.USERS_LISTED, message_code=SuccessCode.USERS_LISTED, data={
            'users': serializer.data,
            'pagination': {
                'total': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
            },
        })


class AddOrganisationUserView(ApiView):
    login_required = True

    def post(self, request):
        data = request.data.get('data', request.data)
        serializer = AddOrganisationUserSerializer(data=data)

        if not serializer.is_valid():
            return _error(
                ErrorMessage.VALIDATION_ERROR,
                message_code=ErrorCode.VALIDATION_ERROR,
                errors=serializer.errors
            )

        vd = serializer.validated_data

        organisation = Organisation.objects.get(id=vd['organisation_id'])
        group = Group.objects.get(id=vd['group_id'])

        full_name = vd.get('full_name', '').strip()
        parts = full_name.split()
        first_name = parts[0] if parts else ''
        last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

        base_username = vd['email'].split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f'{base_username}{counter}'
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=vd['email'],
            password="Temp@123",
            first_name=first_name,
            last_name=last_name,
        )

        UserOrganisationAccess.objects.create(
            user=user,
            organisation=organisation,
            law_firm=organisation.law_firm,
            group=group,
        )

        UserProfile.objects.create(user=user)

        output = OrganisationUserSerializer(
            user, context={'organisation_id': organisation.id}
        )

        return _success(
            SuccessMessage.USER_ADDED_TO_ORG,
            data=output.data,
            message_code=SuccessCode.USER_ADDED_TO_ORG,
            status=201
        )


class UpdateOrganisationUserView(ApiView):
    login_required = True

    def patch(self, request, id):
        data = request.data.get('data', request.data)

        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return _error(
                ErrorMessage.USER_NOT_FOUND,
                message_code=ErrorCode.USER_NOT_FOUND,
                status=404
            )

        serializer = UpdateOrganisationUserSerializer(data=data)

        if not serializer.is_valid():
            return _error(
                ErrorMessage.VALIDATION_ERROR,
                message_code=ErrorCode.VALIDATION_ERROR,
                errors=serializer.errors
            )

        vd = serializer.validated_data

        if 'full_name' in vd:
            full_name = vd.get('full_name', '').strip()
            parts = full_name.split()
            user.first_name = parts[0] if parts else ''
            user.last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

        user.save()

        if 'group_id' in vd and 'organisation_id' in vd:
            group = Group.objects.get(id=vd['group_id'])
            access = UserOrganisationAccess.objects.filter(
                user=user,
                organisation_id=vd['organisation_id']
            ).first()

            if access:
                access.group = group
                access.save()

        return _success(
            SuccessMessage.USER_UPDATED,
            message_code=SuccessCode.USER_UPDATED
        )


class DeleteOrganisationUserView(ApiView):
    login_required = True

    def delete(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return _error(ErrorMessage.USER_NOT_FOUND, message_code=ErrorCode.USER_NOT_FOUND, status=404)

        organisation_id = request.query_params.get('organisation_id')
        if organisation_id:
            UserOrganisationAccess.objects.filter(
                user=user, organisation_id=organisation_id
            ).delete()

        return _success(SuccessMessage.USER_REMOVED, message_code=SuccessCode.USER_REMOVED)


class UserDetailView(ApiView):
    login_required = True

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return _error(ErrorMessage.USER_NOT_FOUND, message_code=ErrorCode.USER_NOT_FOUND, status=404)

        organisation_id = request.query_params.get('organisation_id')
        serializer = OrganisationUserSerializer(user, context={'organisation_id': organisation_id})
        return _success(SuccessMessage.USER_RETRIEVED, message_code=SuccessCode.USER_RETRIEVED, data=serializer.data)


class CurrentUserDetailView(ApiView):
    login_required = True

    def get(self, request):
        user = request.user
        organisations = []
        for access in user.organisation_accesses.all():
            organisations.append({
                'id': access.organisation.id,
                'name': access.organisation.name,
                'law_firm_id': access.organisation.law_firm.id,
                'law_firm_name': access.organisation.law_firm.name,
            })
        return _success(SuccessMessage.USER_RETRIEVED, message_code=SuccessCode.USER_RETRIEVED, data={'organisations': organisations})
