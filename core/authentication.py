from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.authtoken.models import Token


class BoraApiAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_X_TOKEN')
        if not token:
            return None

        try:
            user = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return user, True
