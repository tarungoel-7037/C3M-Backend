import json

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt


def _parse_json(request):
    try:
        return json.loads(request.body or '{}'), None
    except json.JSONDecodeError:
        return None, JsonResponse({'error': 'Invalid JSON body.'}, status=400)


def _user_payload(user):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }


class ApiView(View):
    http_method_names = ['get', 'post']

    def dispatch(self, request, *args, **kwargs):
        if getattr(self, 'login_required', False) and not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required.'}, status=401)
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
            return JsonResponse(
                {'error': 'username, email, and password are required.'},
                status=400,
            )

        if password != confirm_password:
            return JsonResponse({'error': 'Passwords do not match.'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists.'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists.'}, status=400)

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        try:
            validate_password(password, user=user)
        except ValidationError as exc:
            return JsonResponse({'error': list(exc.messages)}, status=400)

        user.set_password(password)
        user.save()
        login(request, user)

        return JsonResponse(
            {'message': 'User created successfully.', 'user': _user_payload(user)},
            status=201,
        )


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(ApiView):
    def post(self, request):
        data, error_response = _parse_json(request)
        if error_response:
            return error_response

        username = (data.get('username') or '').strip()
        password = data.get('password') or ''

        if not username or not password:
            return JsonResponse(
                {'error': 'username and password are required.'},
                status=400,
            )

        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse({'error': 'Invalid credentials.'}, status=401)

        login(request, user)
        return JsonResponse(
            {'message': 'Login successful.', 'user': _user_payload(user)}
        )


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(ApiView):
    login_required = True

    def post(self, request):
        logout(request)
        return JsonResponse({'message': 'Logout successful.'})


class ProfileView(ApiView):
    login_required = True

    def get(self, request):
        return JsonResponse({'user': _user_payload(request.user)})


@method_decorator(csrf_exempt, name='dispatch')
class ChangePasswordView(ApiView):
    login_required = True

    def post(self, request):
        data, error_response = _parse_json(request)
        if error_response:
            return error_response

        old_password = data.get('old_password') or ''
        new_password = data.get('new_password') or ''
        confirm_password = data.get('confirm_password') or ''

        if not old_password or not new_password:
            return JsonResponse(
                {'error': 'old_password and new_password are required.'},
                status=400,
            )

        if not request.user.check_password(old_password):
            return JsonResponse({'error': 'Old password is incorrect.'}, status=400)

        if new_password != confirm_password:
            return JsonResponse({'error': 'Passwords do not match.'}, status=400)

        try:
            validate_password(new_password, user=request.user)
        except ValidationError as exc:
            return JsonResponse({'error': list(exc.messages)}, status=400)

        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)

        return JsonResponse({'message': 'Password changed successfully.'})
