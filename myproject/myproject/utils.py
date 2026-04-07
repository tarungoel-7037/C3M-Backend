import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import AccessToken

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


def _get_user_from_token(request):
    token = request.COOKIES.get('access_token')
    if not token:
        return None
    try:
        validated = AccessToken(token)
        return User.objects.get(id=validated['user_id'])
    except Exception:
        return None


@method_decorator(csrf_exempt, name='dispatch')
class ApiView(View):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def dispatch(self, request, *args, **kwargs):
        if getattr(self, 'login_required', False):
            user = _get_user_from_token(request)
            if user is None:
                return _error(ErrorMessage.AUTH_REQUIRED, message_code=ErrorCode.AUTH_REQUIRED, status=401)
            request.user = user
        return super().dispatch(request, *args, **kwargs)
