from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.tokens import AccessToken


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
