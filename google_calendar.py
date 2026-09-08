import os
import datetime
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def limpiar_llave_privada(key: str) -> str:
    if not key:
        return key
    # Eliminar comillas externas accidentales y corregir saltos de línea
    key = str(key).strip()
    if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
        key = key[1:-1]
    return key.replace("\\n", "\n").strip()

class GoogleCalendarManager:
    def __init__(self, credentials_path="credentials.json"):
        self.scopes = ["https://www.googleapis.com/auth/calendar"]
        
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            if "private_key" in creds_dict:
                creds_dict["private_key"] = limpiar_llave_privada(creds_dict["private_key"])
                
            self.creds = Credentials.from_service_account_info(
                creds_dict, 
                scopes=self.scopes
            )
        elif os.path.exists(credentials_path):
            self.creds = Credentials.from_service_account_file(
                credentials_path, 
                scopes=self.scopes
            )
        else:
            raise FileNotFoundError("No se encontraron credenciales válidas en Secrets ni en credentials.json")

        self.service = build("calendar", "v3", credentials=self.creds)

    def crear_evento(self, calendar_id, resumen, descripcion, fecha_inicio):
        fecha_fin = fecha_inicio + datetime.timedelta(hours=1)
        
        evento = {
            'summary': resumen,
            'description': descripcion,
            'start': {
                'dateTime': fecha_inicio.isoformat(),
                'timeZone': 'America/Caracas', 
            },
            'end': {
                'dateTime': fecha_fin.isoformat(),
                'timeZone': 'America/Caracas',
            },
        }
        
        evento_creado = self.service.events().insert(calendarId=calendar_id, body=evento).execute()
        return evento_creado

    def obtener_eventos_del_dia(self, calendar_id, fecha):
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
                hora_str = start.split('T')[1][:5]
                horas_ocupadas.append(hora_str)

        return horas_ocupadas
