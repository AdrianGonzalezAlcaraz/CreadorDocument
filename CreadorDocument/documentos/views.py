from django.shortcuts import render, get_object_or_404, redirect
from .models import Documento
from .forms import DocumentoForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import os
from google.oauth2.credentials import Credentials
from django.conf import settings
import json
from django.http import HttpResponse
import csv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pptx import Presentation
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
import mimetypes

EXTENSION_MAP = {
    'word': 'docx',
    'txt': 'txt',
    'excel': 'xlsx',
    'cal': 'xls',
    'ppt': 'pptx',
    'pdf': 'pdf',
    'html': 'html',
    'php': 'php',
    'css': 'css',
    'js': 'js',
}

def obtener_nombre_archivo_con_extension(titulo, extension):
    EXTENSION_MAP = {
        'word': 'docx',
        'txt': 'txt',
        'excel': 'xlsx',
        'cal': 'xls',
        'ppt': 'pptx',
        'pdf': 'pdf',
        'html': 'html',
        'php': 'php',
        'css': 'css',
        'js': 'js',
    }

    ext_real = EXTENSION_MAP.get(extension.lower(), extension.lower())  # Usa extensión real o la misma si no está en el mapa
    nombre_archivo = f"{titulo}.{ext_real}"
    return nombre_archivo

@login_required
def lista_documentos(request):
    tipo = request.GET.get('tipo')  # word, excel, etc.
    documentos = Documento.objects.filter(usuario=request.user)
    if tipo:
        if tipo == "word":
            documentos = documentos.filter(extension__in=['word', 'txt'])
        else:
            documentos = documentos.filter(extension=tipo)
    return render(request, 'documentos/lista.html', {'documentos': documentos})

@login_required
def crear_documento(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        extension = request.POST.get('extension')
        contenido = request.POST.get('contenido')
        usuario = request.user

        # Generamos el nombre del archivo y la ruta donde se guardará
        nombre_archivo = obtener_nombre_archivo_con_extension(titulo, extension)
        path_archivo = os.path.join(settings.MEDIA_ROOT, nombre_archivo)
        ruta_completa = os.path.join(settings.BASE_DIR, path_archivo)

        # Crear carpeta si no existe
        os.makedirs(os.path.dirname(ruta_completa), exist_ok=True)

        if extension == 'ppt':
            # Crear una nueva presentación de PowerPoint
            prs = Presentation()

            # Asumimos que cada diapositiva en el contenido está separada por dos saltos de línea
            diapositivas = contenido.split('\n\n')  # Cada "diapositiva" separada por doble salto de línea

            for diapositiva in diapositivas:
                slide = prs.slides.add_slide(prs.slide_layouts[1])  # Añadir una diapositiva de tipo título y contenido
                shapes = slide.shapes
                title = shapes.title
                content = shapes.placeholders[1]

                # Título de la diapositiva (puedes personalizarlo)
                title.text = f"Diapositiva {diapositivas.index(diapositiva) + 1}"
                content.text = diapositiva  # El contenido de la diapositiva

            # Guardar el archivo PowerPoint
            prs.save(ruta_completa)

        else:
            # Para otros tipos de documento, guardamos como texto
            with open(ruta_completa, 'w', encoding='utf-8') as f:
                f.write(contenido)

        # Crear el objeto Documento en la base de datos
        documento = Documento.objects.create(
            usuario=usuario,
            titulo=titulo,
            extension=extension,
            archivo_path=path_archivo
        )

        return redirect('editar_documento', doc_id=documento.id)

    return render(request, 'documentos/crear.html')
 

def csv_to_json(csv_data):
    reader = csv.reader(csv_data.splitlines())
    headers = next(reader)  # Asumiendo que la primera fila son los encabezados
    json_data = []

    for row in reader:
        row_data = {}
        for i, header in enumerate(headers):
            row_data[header] = row[i]
        json_data.append(row_data)

    return json_data
@login_required
def editar_documento(request, doc_id):
    documento = get_object_or_404(Documento, id=doc_id)
    if documento.extension in  ['ppt', 'pptx']:  # Verifica que sea presentación
            prs = Presentation()
            prs.save(documento.archivo_path.path)
            return redirect('editar_presentacion', doc_id=documento.id)
    if request.method == 'POST':
        nuevo_contenido = request.POST.get('contenido')
        
        # Si es un archivo JSON (hoja de cálculo o algo similar)
        if documento.extension in ['xlsx', 'excel', 'spreadsheet']:
            # Asegúrate de que el contenido sea válido JSON
            try:
                json_contenido = json.loads(nuevo_contenido)
                with open(documento.archivo_path.path, 'w', encoding='utf-8') as f:
                    json.dump(json_contenido, f, ensure_ascii=False, indent=4)
            except json.JSONDecodeError:
                # Manejar el error si no se puede convertir a JSON
                return render(request, 'documentos/error.html', {'mensaje': 'Error al guardar el contenido. Formato JSON inválido.'})

        # Para otros documentos de texto
        else:
            with open(documento.archivo_path.path, 'w', encoding='utf-8') as f:
                f.write(nuevo_contenido)
        
        return redirect('lista_documentos')

    # Leer contenido de archivo
    if documento.extension in ['html', 'css', 'JavaScript', 'php']:
        with open(documento.archivo_path.path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        return render(request, 'documentos/editar_codigo.html', {'documento': documento, 'contenido': contenido})
    elif documento.extension in ['xlsx', 'excel', 'spreadsheet']:
        # Para Luckysheet, lo ideal es cargar un JSON o una plantilla vacía
        with open(documento.archivo_path.path, 'r', encoding='utf-8') as f:
            contenido = f.read().strip()
        
        # Si no hay contenido, inicializar un contenido vacío por defecto
        if contenido:
            try:
            # Intentar parsear como JSON para comprobar que ya está en formato válido
                json.loads(contenido)
            except json.JSONDecodeError:
            # Si no es JSON, entonces sí intentamos convertirlo desde CSV
                try:
                    contenido_json = csv_to_json(contenido)
                    contenido = json.dumps([{
                    "name": "Hoja1",
                    "color": "",
                    "index": 0,
                    "status": 1,
                    "order": 0,
                    "celldata": contenido_json,
                    "row": 30,
                    "column": 15
                    }])
                except Exception as e:
                    print("Error al convertir CSV a JSON:", e)
                contenido = '[{ "name": "Hoja1", "celldata": [] }]'
        else:
            contenido = '[{ "name": "Hoja1", "celldata": [] }]'
        return render(request, 'documentos/editar_excel.html', {'documento': documento, 'contenido': contenido})
    else:
        with open(documento.archivo_path.path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        return render(request, 'documentos/editar_wysiwyg.html', {'documento': documento, 'contenido': contenido})
@login_required
@csrf_exempt  # Asegúrate de manejar el CSRF token correctamente en producción
def guardar_hoja_calculo(request, doc_id):
    documento = get_object_or_404(Documento, id=doc_id)
    
    if request.method == 'POST':
        try:
            # Recibimos los datos JSON de la solicitud
            datos_json = json.loads(request.body)
            contenido = datos_json.get('contenido')
            
            if contenido:
                # Guardar el contenido en el archivo correspondiente
                with open(documento.archivo_path.path, 'w', encoding='utf-8') as f:
                    f.write(contenido)  # Escribe el contenido nuevo en el archivo
                with open(documento.archivo_path.path, 'r', encoding='utf-8') as f:
                    verificacion = f.read()
                    print("Contenido después de guardar:", verificacion)

                return JsonResponse({"status": "success", "message": "Guardado exitosamente"})
            else:
                return JsonResponse({"status": "error", "message": "No se proporcionó contenido"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error al guardar: {str(e)}"})
    
    return JsonResponse({"status": "error", "message": "Método no permitido"})

def editar_presentacion(request, doc_id):
    doc = get_object_or_404(Documento, id=doc_id)
    ruta = doc.archivo_path.path
    print(f"Ruta completa del archivo: {ruta}")

    # Intenta abrir el archivo de presentación
    try:
        prs = Presentation(ruta)
    except Exception as e:
        # Si el archivo no es válido, capturamos el error
        print(f"Error al abrir el archivo PPT: {e}")
        return render(request, "documentos/error.html", {
            "mensaje": "El archivo de presentación no se pudo abrir correctamente."
        })
    
    # Si el archivo no tiene diapositivas, creamos una nueva diapositiva
    if len(prs.slides) == 0:
        print("El archivo está vacío, creando una diapositiva de ejemplo.")
        slide_layout = prs.slide_layouts[0]  # Título y contenido
        slide = prs.slides.add_slide(slide_layout)
        title = slide.shapes.title
        title.text = "Primera diapositiva"
        content = slide.shapes.placeholders[1]
        content.text = "Este es un contenido de ejemplo para la diapositiva."

        # Guardamos el archivo con la nueva diapositiva
        prs.save(ruta)
    
    # Extraer los datos de las diapositivas para pasarlos a la plantilla
    slides_data = []
    for i, slide in enumerate(prs.slides):
        texto = []
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                texto.append(shape.text)
        slides_data.append({"index": i, "contenido": texto})

    print(f"Slides data: {slides_data}")
    
    return render(request, "documentos/editar_presentacion.html", {
        "documento": doc,
        "slides": slides_data,
    })
def guardar_diapositiva(request, doc_id, slide_index):
    # Obtén el documento y la diapositiva
    documento = get_object_or_404(Documento, id=doc_id)

    # Aquí iría la lógica para guardar la diapositiva (por ejemplo, guardar el contenido)
    # Asume que la diapositiva está en un formato adecuado para ser procesada.
    slide_data = {
        'doc_id': doc_id,
        'slide_index': slide_index
    }

    # Lógica para guardar el contenido de la diapositiva
    # Tu lógica de guardar la diapositiva va aquí...

    return render(request, 'guardar_diapositiva.html', {'slide_data': slide_data})
def eliminar_diapositiva(request, doc_id, slide_index):
    # Obtén el documento
    documento = get_object_or_404(Documento, id=doc_id)

    # Lógica para eliminar la diapositiva (ejemplo: eliminar un elemento de una lista)
    if slide_index < len(documento.slides):
        documento.slides.pop(slide_index)
        documento.save()

    # Redirigir a una página de edición de presentación después de eliminar
    return redirect('editar_presentacion', doc_id=doc_id)


def exportar_a_drive(request, doc_id):
    documento = get_object_or_404(Documento, id=doc_id)
    archivo_path = documento.archivo_path.path

    creds_data = request.session.get('credentials')
    if not creds_data:
        return HttpResponse("No hay credenciales en sesión.")

    creds = Credentials(
        token=creds_data['token'],
        refresh_token=creds_data.get('refresh_token'),
        token_uri=creds_data['token_uri'],
        client_id=creds_data['client_id'],
        client_secret=creds_data['client_secret'],
        scopes=creds_data['scopes'],
    )

    service = build('drive', 'v3', credentials=creds)

    ext_real = EXTENSION_MAP.get(documento.extension, 'bin')
    nombre_archivo = f"{documento.titulo}.{ext_real}"

    mime_type, _ = mimetypes.guess_type(nombre_archivo)

    file_metadata = {
        'name': nombre_archivo,
        'mimeType': mime_type or 'application/octet-stream',
    }

    media = MediaFileUpload(archivo_path, mimetype=mime_type, resumable=True)

    service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return redirect('lista_documentos')


def obtener_servicio_drive(request):
    creds_data = request.session.get('credentials')
    if not creds_data:
        print("No hay credenciales almacenadas en la sesión.")
        return None

    try:
        creds = Credentials(
            token=creds_data.get('token'),
            refresh_token=creds_data.get('refresh_token'),
            token_uri=creds_data.get('token_uri'),
            client_id=creds_data.get('client_id'),
            client_secret=creds_data.get('client_secret'),
            scopes=creds_data.get('scopes'),
        )
        servicio = build('drive', 'v3', credentials=creds)
        return servicio
    except Exception as e:
        print(f"Error al crear el servicio de Drive: {e}")
        return None


def borrar_archivo_drive(request, nombre_archivo_con_extension):
    servicio = obtener_servicio_drive(request)
    if not servicio:
        return False

    # Busca el archivo por nombre exacto
    resultados = servicio.files().list(
        q=f"name = '{nombre_archivo_con_extension}' and trashed = false",
        spaces='drive',
        fields="files(id, name)"
    ).execute()

    archivos = resultados.get('files', [])

    if not archivos:
        print(f"No se encontró ningún archivo con el nombre: {nombre_archivo_con_extension}")
        return False

    for archivo in archivos:
        try:
            servicio.files().delete(fileId=archivo['id']).execute()
            print(f"Archivo eliminado: {archivo['name']}")
        except Exception as e:
            print(f"Error al eliminar el archivo {archivo['name']}: {e}")

            return False

    return True

def eliminar_archivo(request, titulo, extension, doc_id):
    servicio = obtener_servicio_drive(request)
    if not servicio:
        return HttpResponse("No se pudo conectar a Google Drive.")

    nombre_archivo_con_extension = obtener_nombre_archivo_con_extension(titulo, extension)

    # Aquí llamas a la función que borra el archivo por nombre con extensión correcta
    borrado = borrar_archivo_drive(request, nombre_archivo_con_extension)
    if borrado:
        return HttpResponse("Archivo eliminado exitosamente.")
def borrar_documento(request, doc_id):
    try:
        documento = Documento.objects.get(id=doc_id)
    except Documento.DoesNotExist:
        messages.error(request, "Documento no encontrado.")
        return redirect('lista_documentos')
    if request.method == 'POST':
            documento = get_object_or_404(Documento, id=doc_id)
            # 1. Borrar archivo local
            archivo_path = documento.archivo_path.path
            if os.path.exists(archivo_path):
                os.remove(archivo_path)
    servicio = obtener_servicio_drive(request)
    if not servicio:
        messages.error(request, "No se pudo conectar a Google Drive.")
        return redirect('lista_documentos')

    # Usa la función para obtener nombre con extensión correcta
    nombre_archivo_con_extension = obtener_nombre_archivo_con_extension(documento.titulo, documento.extension)

    exito = borrar_archivo_drive(request, nombre_archivo_con_extension)
    if exito:
        documento.delete()
        messages.success(request, "Documento borrado correctamente.")
    else:
        messages.error(request, "No se pudo borrar el documento en Google Drive.")
