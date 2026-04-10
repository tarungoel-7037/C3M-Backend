from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import LawFirm, UserLawFirmAccess, UserProfile
from accounts.serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    SignupSerializer,
    UserProfileOutputSerializer,
    UserSerializer,
)
from myproject.constants import AuditAction, AuditModule, ErrorCode, ErrorMessage, SuccessCode, SuccessMessage
from myproject.utils import ApiView, _error, _success, log_action


class SignupView(ApiView):
    def post(self, request):
        data = request.data.get('data', request.data)
        serializer = SignupSerializer(data=data)
        if not serializer.is_valid():
            return _error(ErrorMessage.VALIDATION_ERROR, message_code=ErrorCode.VALIDATION_ERROR, errors=serializer.errors)

        vd = serializer.validated_data
        user = User(
            username=vd['username'],
            email=vd['email'],
            first_name=vd.get('first_name', ''),
            last_name=vd.get('last_name', ''),
        )
        user.set_password(vd['password'])
        user.save()
        UserProfile.objects.create(user=user)

        group = Group.objects.get(name=vd['group'])
        law_firm = LawFirm.objects.get(id=vd['law_firm_id'])
        UserLawFirmAccess.objects.create(
            user=user,
            law_firm=law_firm,
            group=group,
        )

        log_action(
            request,
            action=AuditAction.CREATE_USER,
            module=AuditModule.USERS,
            obj_id=user.id,
            action_details=f'Created user {user.username}',
            related_object_id=law_firm.id,
        )

        return _success(SuccessMessage.USER_CREATED, data=UserSerializer(user).data, message_code=SuccessCode.USER_CREATED, status=201)


class LoginView(ApiView):
    def post(self, request):
        data = request.data.get('data', request.data)
        serializer = LoginSerializer(data=data)
        if not serializer.is_valid():
            return _error(ErrorMessage.VALIDATION_ERROR, message_code=ErrorCode.VALIDATION_ERROR, errors=serializer.errors)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return _error(ErrorMessage.INVALID_CREDENTIALS, message_code=ErrorCode.INVALID_CREDENTIALS, status=401)

        user = authenticate(request, username=user.username, password=password)
        if user is None:
            return _error(ErrorMessage.INVALID_CREDENTIALS, message_code=ErrorCode.INVALID_CREDENTIALS, status=401)

        refresh = RefreshToken.for_user(user)
        response = _success(SuccessMessage.LOGIN, data=UserSerializer(user).data, message_code=SuccessCode.LOGIN)
        response.set_cookie('access_token', str(refresh.access_token), httponly=True, samesite='Lax')
        response.set_cookie('refresh_token', str(refresh), httponly=True, samesite='Lax')
        response.delete_cookie('sessionid')
        return response


class LogoutView(ApiView):
    login_required = True

    def post(self, request):
        response = _success(SuccessMessage.LOGOUT, message_code=SuccessCode.LOGOUT)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        response.delete_cookie('csrftoken')
        return response


class ProfileView(ApiView):
    login_required = True

    def get(self, request):
        user = request.user
        profile = getattr(user, 'profile', None)

        law_firms = []
        all_permissions = set()
        is_law_firm_admin = False

        for access in user.law_firm_accesses.select_related('law_firm', 'group').prefetch_related(
            'group__profile__permissions'
        ):
            group_profile = getattr(access.group, 'profile', None)
            group_permissions = []
            if group_profile:
                group_permissions = list(
                    group_profile.permissions.values_list('codename', flat=True)
                )
                all_permissions.update(group_permissions)
                if 'law_admin' in access.group.name:
                    is_law_firm_admin = True

            law_firms.append({
                'id': access.law_firm.id,
                'name': access.law_firm.name,
                'group': {
                    'id': access.group.id,
                    'name': access.group.name,
                    'display_name': group_profile.display_name if group_profile else '',
                    'group_entity_type': group_profile.group_entity_type if group_profile else '',
                    'permissions': sorted(group_permissions),
                },
            })

        organisations = []
        for access in user.organisation_accesses.select_related('organisation', 'group').prefetch_related(
            'group__profile__permissions'
        ):
            group_profile = getattr(access.group, 'profile', None)
            group_permissions = []
            if group_profile:
                group_permissions = list(
                    group_profile.permissions.values_list('codename', flat=True)
                )
                all_permissions.update(group_permissions)

            organisations.append({
                'id': access.organisation.id,
                'name': access.organisation.name,
                'group': {
                    'id': access.group.id,
                    'name': access.group.name,
                    'display_name': group_profile.display_name if group_profile else '',
                    'group_entity_type': group_profile.group_entity_type if group_profile else '',
                    'permissions': sorted(group_permissions),
                },
            })

        profile_data = {
            'id': user.id,
            'full_name': ' '.join(filter(None, [user.first_name, user.last_name])) or user.username,
            'email': user.email,
            'contact_number': profile.contact_number if profile else None,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'law_firms': law_firms,
            'organisations': organisations,
            'is_law_firm_admin': is_law_firm_admin,
            'permissions': sorted(all_permissions),
            'created_at': profile.created_at.isoformat() if profile else None,
            'updated_at': profile.updated_at.isoformat() if profile else None,
        }

        serializer = UserProfileOutputSerializer(profile_data)
        return _success(SuccessMessage.PROFILE_RETRIEVED, message_code=SuccessCode.PROFILE_RETRIEVED, data=serializer.data)


class ChangePasswordView(ApiView):
    login_required = True

    def post(self, request):
        data = request.data.get('data', request.data)
        serializer = ChangePasswordSerializer(data=data)
        if not serializer.is_valid():
            return _error(ErrorMessage.VALIDATION_ERROR, message_code=ErrorCode.VALIDATION_ERROR, errors=serializer.errors)

        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not request.user.check_password(old_password):
            return _error(ErrorMessage.WRONG_OLD_PASSWORD, message_code=ErrorCode.WRONG_OLD_PASSWORD)

        try:
            validate_password(new_password, user=request.user)
        except ValidationError as exc:
            return _error(ErrorMessage.PASSWORD_INVALID, message_code=ErrorCode.PASSWORD_INVALID, errors={'password': list(exc.messages)})

        request.user.set_password(new_password)
        request.user.save()

        log_action(
            request,
            action=AuditAction.CHANGE_PASSWORD,
            module=AuditModule.USERS,
            obj_id=request.user.id,
            action_details=f'Changed password for user {request.user.username}',
        )

        return _success(SuccessMessage.PASSWORD_CHANGED, message_code=SuccessCode.PASSWORD_CHANGED)
