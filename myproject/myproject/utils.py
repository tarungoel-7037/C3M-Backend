from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from myproject.constants import ErrorCode, SuccessCode


def _success(message, data=None, message_code=SuccessCode.DEFAULT, status=200):
    return Response({
        'status': True,
        'message_code': message_code,
        'message': message,
        'data': data or {},
        'errors': {},
    }, status=status)


def _error(message, message_code=ErrorCode.DEFAULT, errors=None, status=400):
    return Response({
        'status': False,
        'message_code': message_code,
        'message': message,
        'data': {},
        'errors': errors or {},
    }, status=status)


class CookieJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('access_token')
        if not token:
            return None
        try:
            validated = AccessToken(token)
            user = User.objects.get(id=validated['user_id'])
            return (user, validated)
        except Exception:
            return None


class ApiView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    login_required = False

    def get_permissions(self):
        if getattr(self, 'login_required', False):
            return [IsAuthenticated()]
        return []
