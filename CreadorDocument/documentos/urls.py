from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_documentos, name='lista_documentos'),
    path('crear/', views.crear_documento, name='crear_documento'),
    path('editar/<int:doc_id>/', views.editar_documento, name='editar_documento'),
    path('documentos/guardar/<int:doc_id>/', views.guardar_hoja_calculo, name='guardar_hoja_calculo'),
    path('documento/<int:doc_id>/editar_ppt/', views.editar_presentacion, name='editar_presentacion'),
    path('guardar_diapositiva/<int:doc_id>/<int:slide_index>/', views.guardar_diapositiva, name='guardar_diapositiva'),
    path('eliminar_diapositiva/<int:doc_id>/<int:slide_index>/', views.eliminar_diapositiva, name='eliminar_diapositiva'),
    path('documentos/<int:doc_id>/exportar/', views.exportar_a_drive, name='exportar_a_drive'),
    path('documentos/borrar/<int:doc_id>/', views.borrar_documento, name='borrar_documento'),
]
