# oauth.py
import os
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Cargar las credenciales de OAuth 2.0 desde el archivo JSON
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), 'credentials/client_secret.json')
API_NAME = 'drive'  # Cambia a 'gmail' si solo necesitas Gmail
API_VERSION = 'v3'  # Usa 'v1' para Gmail, 'v3' para Google Drive

# Define los alcances que necesitas
SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/gmail.send']

# Función para obtener las credenciales y realizar la autenticación
def get_credentials():
    credentials = None
    # El archivo token.json almacena el token de acceso del usuario y es creado automáticamente cuando el flujo de autorización es completado por primera vez.
    token_path = os.path.join(os.path.dirname(__file__), 'credentials/token.json')

    # Si ya tenemos un token guardado, lo cargamos
    if os.path.exists(token_path):
        credentials, project = google.auth.load_credentials_from_file(token_path)

    # Si no tenemos credenciales (o han expirado), iniciamos el flujo de autorización
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)

        # Guardamos las credenciales en el archivo token.json
        with open(token_path, 'w') as token:
            token.write(credentials.to_json())

    return credentials

# Función para obtener el servicio de Gmail o Google Drive
def get_service(api_name=API_NAME, api_version=API_VERSION):
    credentials = get_credentials()
    service = build(api_name, api_version, credentials=credentials)
    return service