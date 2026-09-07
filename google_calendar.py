import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

class GoogleCalendarManager:
    def __init__(self, credentials_path="credentials.json"):
        # Permisos necesarios para gestionar el calendario
        self.scopes = ['https://www.googleapis.com/auth/calendar']
        # Autenticación con el archivo de credenciales
        self.creds = Credentials.from_service_account_file(credentials_path, scopes=self.scopes)
        self.service = build('calendar', 'v3', credentials=self.creds)

    def crear_evento(self, calendar_id, resumen, descripcion, fecha_inicio, duracion_minutos=30):
        """
        Crea un evento en el Google Calendar especificado.
        fecha_inicio debe ser un objeto datetime.
        """
        fecha_fin = fecha_inicio + datetime.timedelta(minutes=duracion_minutos)
        
        # Formato ISO requerido por la API de Google
        evento = {
            'summary': resumen,
            'description': descripcion,
            'start': {
                'dateTime': fecha_inicio.isoformat(),
                'timeZone': 'America/Caracas', # Cambia a tu zona horaria si es diferente
            },
            'end': {
                'dateTime': fecha_fin.isoformat(),
                'timeZone': 'America/Caracas',
            },
        }

        # Insertar evento en el calendario
        evento_creado = self.service.events().insert(calendarId=calendar_id, body=evento).execute()
        return evento_creado.get('htmlLink')
    def obtener_eventos_del_dia(self, calendar_id, fecha):
        """Obtiene todas las horas ocupadas de un día específico."""
        inicio_dia = datetime.datetime.combine(fecha, datetime.time.min).isoformat() + 'Z'
        fin_dia = datetime.datetime.combine(fecha, datetime.time.max).isoformat() + 'Z'

        events_result = self.service.events().list(
            calendarId=calendar_id,
            timeMin=inicio_dia,
            timeMax=fin_dia,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        eventos = events_result.get('items', [])
        horas_ocupadas = []

        for evento in eventos:
            start = evento['start'].get('dateTime', evento['start'].get('date'))
            if 'T' in start:
                # Extrae la hora exacta (HH:MM)
                hora_str = start.split('T')[1][:5]
                horas_ocupadas.append(hora_str)

        return horas_ocupadas