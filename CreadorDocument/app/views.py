"""
Definition of views.
"""
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
import json
from urllib.parse import urlencode
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.http import HttpRequest
from .oauth import get_service 
from django.conf import settings
from django.http import HttpResponse
from app.models import Usuario
from google.oauth2 import id_token
from .forms import LoginForm
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_oauthlib.flow import Flow
from social_django.models import UserSocialAuth
from django.contrib.auth.models import User
from django.contrib.auth import login, get_user_model
from google.auth.transport import requests as google_requests
import warnings

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/login.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect('lista_documentos')
    form = LoginForm(request.POST or None)
    error = None

    # Asegúrate de que `settings.GOOGLE_OAUTH_SCOPES` contiene el orden correcto
    google_oauth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?" +
        urlencode({
            "response_type": "code",
            "client_id": settings.CLIENT_ID,
            "redirect_uri": "https://creadordocument.onrender.com/oauth2callback/",
            "scope": " ".join(settings.GOOGLE_OAUTH_SCOPES),
            "access_type": "offline",
            "prompt": "select_account",
        })
    )

    if request.method == 'POST':
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']
            try:
                user = Usuario.objects.get(email=identifier)
            except Usuario.DoesNotExist:
                try: 
                    user = Usuario.objects.get(username=identifier)
                except Usuario.DoesNotExist:
                    user = authenticate(request, username=identifier, password=password)

            user = authenticate(request, username=identifier, password=password)
            if user is not None:
                login(request, user)
                return redirect('lista_documentos')  # Cambia por tu URL de destino
            else:
                error = "Correo electrónico o contraseña incorrectos."

    return render(request, 'app/login.html', {'form': form, 'error': error, 'google_oauth_url': google_oauth_url})


def crear_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')

        if not nombre or not correo or not contrasena:
            messages.error(request, "Todos los campos son obligatorios.")
            return render(request, 'crear_usuario.html')

        if Usuario.objects.filter(username=nombre).exists():
            messages.error(request, "El nombre de usuario ya existe.")
            return render(request, 'app/crear_usuario.html')

        if Usuario.objects.filter(email=correo).exists():
            messages.error(request, "El correo electrónico ya está en uso.")
            return render(request, 'app/crear_usuario.html')

        user = Usuario.objects.create_user(username=nombre, email=correo, password=contrasena)
        user.save()
        messages.success(request, "Usuario creado correctamente.")
        return redirect('registro')  # Usa el nombre de URL correspondiente
    #id de google pro-pulsar-459412-k3
    return render(request, 'app/crear_usuario.html')
    #return render(request, 'app/login.html')


'''def oauth2callback(request):
    code = request.GET.get('code')
    if not code:
        return HttpResponse("Código de autorización faltante.")

    # Crea el flujo OAuth
    flow = Flow.from_client_secrets_file(
        settings.CLIENT_SECRET_FILE,
        scopes=settings.GOOGLE_OAUTH_SCOPES,
        redirect_uri="https://creadordocument.onrender.com/oauth2callback/"
    )

    # Evita el warning de "Scope has changed"
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=r"Scope has changed.*",
            category=Warning,
            module="oauthlib.oauth2.rfc6749.parameters"
        )
        flow.fetch_token(code=code)

    credentials = flow.credentials
    request.session['google_credentials'] = credentials.to_json()
    if not credentials or not credentials.id_token:
        return HttpResponse("No se pudo obtener el id_token.")

    try:
        # Decodifica el id_token para extraer info del usuario
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            google_requests.Request(),
            credentials.client_id
        )
    except Exception as e:
        return HttpResponse(f"Error al verificar el id_token: {e}")

    google_id = id_info.get('sub')
    google_email = id_info.get('email')

    if not google_id or not google_email:
        return HttpResponse("Faltan datos del token de Google.")

    Usuario = get_user_model()

    try:
        # Intenta obtener el usuario social si ya existe
        user_social = UserSocialAuth.objects.get(provider='google', uid=google_id)
        user = user_social.user
    except UserSocialAuth.DoesNotExist:
        try:
            # Intenta encontrar un usuario por email
            user = Usuario.objects.get(email=google_email)
        except Usuario.DoesNotExist:
            # Crea un nuevo usuario si no existe
            user = Usuario.objects.create_user(
                username=google_email.split('@')[0],
                email=google_email,
                password=None
            )
        # Crea el vínculo social
        UserSocialAuth.objects.create(user=user, provider='google', uid=google_id)

    # Inicia sesión con Django
    user.backend = 'social_core.backends.google.GoogleOAuth2'

    # Opcional: guarda las credenciales si planeas usarlas para Gmail/Drive
    user.google_credentials = json.dumps({
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    })
    user.save()
    login(request, user)
    return redirect('lista_documentos')  # o la URL de tu elección'''
def oauth2callback(request):
    try:
        code = request.GET.get('code')
        if not code:
            return HttpResponse("Código de autorización faltante.")

        flow = Flow.from_client_secrets_file(
            settings.CLIENT_SECRET_FILE,
            scopes=settings.GOOGLE_OAUTH_SCOPES,
            redirect_uri="https://creadordocument.onrender.com/oauth2callback/"
        )

        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r"Scope has changed.*",
                category=Warning,
                module="oauthlib.oauth2.rfc6749.parameters"
            )
            flow.fetch_token(code=code)

        credentials = flow.credentials
        request.session['google_credentials'] = credentials.to_json()
        if not credentials or not credentials.id_token:
            return HttpResponse("No se pudo obtener el id_token.")

        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            google_requests.Request(),
            credentials.client_id
        )

        google_id = id_info.get('sub')
        google_email = id_info.get('email')

        if not google_id or not google_email:
            return HttpResponse("Faltan datos del token de Google.")

        Usuario = get_user_model()

        try:
            user_social = UserSocialAuth.objects.get(provider='google', uid=google_id)
            user = user_social.user
        except UserSocialAuth.DoesNotExist:
            try:
                user = Usuario.objects.get(email=google_email)
            except Usuario.DoesNotExist:
                user = Usuario.objects.create_user(
                    username=google_email.split('@')[0],
                    email=google_email,
                    password=None
                )
            UserSocialAuth.objects.create(user=user, provider='google', uid=google_id)

        user.backend = 'social_core.backends.google.GoogleOAuth2'

        # Verifica que el modelo Usuario tenga este campo:
        if hasattr(user, 'google_credentials'):
            user.google_credentials = json.dumps({
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            })
            user.save()

        login(request, user)
        return redirect('lista_documentos')
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return HttpResponse(f"Error en oauth2callback: {e}<br><pre>{tb}</pre>")
def inicio(request):
    return render(request, 'app/login.html')


@login_required
def configurar_sesion(request):
    usuario_email = request.user.email if request.user.is_authenticated else 'No conectado'
    return render(request, 'app/configurar_sesion.html', {'usuario_email': usuario_email})

@login_required
def desconectar_google(request):
    if 'google_credentials' in request.session:
        del request.session['google_credentials']

    # Cierra la sesión de Django
    logout(request)
    return redirect('inicio')