"""
Definition of urls for CreadorDocument.
"""

from datetime import datetime
from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


'''urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('login/',
         LoginView.as_view
         (
             template_name='app/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context=
             {
                 'title': 'Log in',
                 'year' : datetime.now().year,
             }
         ),
         name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('documentos/', include('documentos.urls')),
]'''
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Vista personalizada de login (mantienes si usas BootstrapAuthenticationForm)
    path('login/', 
         LoginView.as_view(
             template_name='app/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context={
                 'title': 'Log in',
                 'year': datetime.now().year,
             }
         ),
         name='login'),
    
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),

    # Páginas estáticas
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),

    # Página principal: login personalizado
    path('', views.login_view, name='home'),  # <- Aquí redirige a login_view directamente

    # Usuario y documentos
    path('', include('app.urls')),
    path('crear-usuario/', views.crear_usuario, name='crear_usuario'),
    path('documentos/', include('documentos.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
