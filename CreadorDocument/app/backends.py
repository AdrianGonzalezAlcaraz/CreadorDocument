from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from .models import Usuario

#UserModel = get_user_model()

class EmailOrUsernameModelBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None
        # Si el identificador contiene '@', lo tratamos como correo electrónico
        if '@' in username:
            try:
                user = Usuario.objects.get(email=username)  # Busca por email
            except Usuario.DoesNotExist:
                return None
        else:
            try:
                user = Usuario.objects.get(username=username)  # Busca por nombre de usuario
            except Usuario.DoesNotExist:
                return None
        
        if user and user.check_password(password):
            return user
        return None