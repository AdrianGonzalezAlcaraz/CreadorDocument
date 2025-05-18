from django.urls import path
from .views import crear_usuario, login_view, oauth2callback  # registro_view lo defines aparte

urlpatterns = [
    #path('inicio/', login_view, name='login'),
    path('crear_usuario/', crear_usuario, name='crear_usuario'),
    path('registro/', login_view, name='registro'),
    path('oauth2callback/', oauth2callback, name='oauth2callback'),
]