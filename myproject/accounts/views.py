import json

from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from myproject.constants import ErrorCode, ErrorMessage, SuccessCode, SuccessMessage


def _success(message, data=None, message_code=SuccessCode.DEFAULT, status=200):
    return JsonResponse({
        'status': True,
        'message_code': message_code,
        'message': message,
        'data': data or {},
        'errors': {},
    }, status=status)


def _error(message, message_code=ErrorCode.DEFAULT, errors=None, status=400):
    return JsonResponse({
        'status': False,
        'message_code': message_code,
        'message': message,
        'data': {},
        'errors': errors or {},
    }, status=status)


def _parse_json(request):
    try:
        body = json.loads(request.body or '{}')
        return body.get('data', body), None
    except json.JSONDecodeError:
        return None, _error(ErrorMessage.INVALID_JSON, message_code=ErrorCode.INVALID_JSON)


def _user_payload(user):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }


def _get_user_from_token(request):
    token = request.COOKIES.get('access_token')
    if not token:
        return None
    try:
        validated = AccessToken(token)
        return User.objects.get(id=validated['user_id'])
    except Exception:
        return None


class ApiView(View):
    http_method_names = ['get', 'post']

    def dispatch(self, request, *args, **kwargs):
        if getattr(self, 'login_required', False):
            user = _get_user_from_token(request)
            if user is None:
                return _error(ErrorMessage.AUTH_REQUIRED, message_code=ErrorCode.AUTH_REQUIRED, status=401)
            request.user = user
        return super().dispatch(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class SignupView(ApiView):
    def post(self, request):
        data, error_response = _parse_json(request)
        if error_response:
            return error_response

        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip()
        password = data.get('password') or ''
        confirm_password = data.get('confirm_password') or ''
        first_name = (data.get('first_name') or '').strip()
        last_name = (data.get('last_name') or '').strip()

        if not username or not email or not password:
            return _error('username, email, and password are required.', message_code=ErrorCode.MISSING_FIELDS)

        if password != confirm_password:
            return _error(ErrorMessage.PASSWORD_MISMATCH, message_code=ErrorCode.PASSWORD_MISMATCH)

        if User.objects.filter(username=username).exists():
            return _error(ErrorMessage.USERNAME_EXISTS, message_code=ErrorCode.USERNAME_EXISTS)

        if User.objects.filter(email=email).exists():
            return _error(ErrorMessage.EMAIL_EXISTS, message_code=ErrorCode.EMAIL_EXISTS)

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        try:
            validate_password(password, user=user)
        except ValidationError as exc:
            return _error(ErrorMessage.PASSWORD_INVALID, message_code=ErrorCode.PASSWORD_INVALID, errors={'password': list(exc.messages)})

        user.set_password(password)
        user.save()

        return _success(SuccessMessage.USER_CREATED, data=_user_payload(user), message_code=SuccessCode.USER_CREATED, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(ApiView):
    def post(self, request):
        data, error_response = _parse_json(request)
        if error_response:
            return error_response

        email = (data.get('email') or '').strip()
        password = data.get('password') or ''

        if not email or not password:
            return _error('email and password are required.', message_code=ErrorCode.MISSING_FIELDS)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return _error(ErrorMessage.INVALID_CREDENTIALS, message_code=ErrorCode.INVALID_CREDENTIALS, status=401)

        user = authenticate(request, username=user.username, password=password)
        if user is None:
            return _error(ErrorMessage.INVALID_CREDENTIALS, message_code=ErrorCode.INVALID_CREDENTIALS, status=401)

        get_token(request)
        refresh = RefreshToken.for_user(user)
        response = _success(SuccessMessage.LOGIN, data=_user_payload(user), message_code=SuccessCode.LOGIN)
        response.set_cookie('access_token', str(refresh.access_token), httponly=True, samesite='Lax')
        response.set_cookie('refresh_token', str(refresh), httponly=True, samesite='Lax')
        response.delete_cookie('sessionid')
        return response


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(ApiView):
    login_required = True

    def post(self, _request):
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

        return _success(SuccessMessage.PROFILE_RETRIEVED, message_code=SuccessCode.PROFILE_RETRIEVED, data={
            'id': user.id,
            'full_name': f'{user.first_name} {user.last_name}'.strip() or user.username,
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
        })


@method_decorator(csrf_exempt, name='dispatch')
class ChangePasswordView(ApiView):
    login_required = True

    def post(self, request):
        data, error_response = _parse_json(request)
        if error_response:
            return error_response

        old_password = data.get('old_password') or ''
        new_password = data.get('new_password') or ''

        if not old_password or not new_password:
            return _error('old_password and new_password are required.', message_code=ErrorCode.MISSING_FIELDS)

        if not request.user.check_password(old_password):
            return _error(ErrorMessage.WRONG_OLD_PASSWORD, message_code=ErrorCode.WRONG_OLD_PASSWORD)

        try:
            validate_password(new_password, user=request.user)
        except ValidationError as exc:
            return _error(ErrorMessage.PASSWORD_INVALID, message_code=ErrorCode.PASSWORD_INVALID, errors={'password': list(exc.messages)})

        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)

        return _success(SuccessMessage.PASSWORD_CHANGED, message_code=SuccessCode.PASSWORD_CHANGED)
