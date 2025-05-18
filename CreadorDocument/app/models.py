"""
Definition of models.
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError("El correo electronico es obligatorio.")
        if not username:
            raise ValueError("El nombre de usuario es obligatorio.")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)  # Hashea la contraseña
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Usuario(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
class GoogleCredentials(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.TextField(blank=True, null=True)           # access token
    refresh_token = models.TextField(blank=True, null=True)   # refresh token
    token_uri = models.TextField(blank=True, null=True)
    client_id = models.TextField(blank=True, null=True)
    client_secret = models.TextField(blank=True, null=True)
    scopes = models.TextField(blank=True, null=True)          # por ejemplo: "https://www.googleapis.com/auth/drive"
    expiry = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Credenciales Google de {self.user.email}"