from django.urls import path
from .views import crear_usuario, login_view, oauth2callback, inicio, configurar_sesion, desconectar_google  

urlpatterns = [
    path('', inicio, name='inicio'),
    #path('inicio/', login_view, name='login'),
    path('crear_usuario/', crear_usuario, name='crear_usuario'),
    path('registro/', login_view, name='registro'),
    path('oauth2callback/', oauth2callback, name='oauth2callback'),
    path('configurar_sesion/', configurar_sesion, name='configurar_sesion'),
    path('desconectar_google/', desconectar_google, name='desconectar_google'),
]