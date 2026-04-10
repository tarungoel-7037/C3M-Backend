from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from django.utils.timezone import now
from myapp.models import AuditAuditlog


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
    
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def get_user_role(user):
    if not user:
        return "Anonymous"
    return user.groups.first().name if user.groups.exists() else "No Role"

def log_action(
    request,
    action,
    module,
    obj_id=None,
    action_details="",
    related_object_id=None,
):
    try:
        user = request.user if request.user.is_authenticated else None

        AuditAuditlog.objects.create(
            created_at=now(),
            updated_at=now(),
            action=action,
            action_details=action_details or action,
            obj_id=obj_id,
            module=module,
            related_object_id=related_object_id,
            performed_by_id=user.id if user else None,
            ip_address=get_client_ip(request)
        )

    except Exception as e:
        print("Audit Log Error:", str(e))


