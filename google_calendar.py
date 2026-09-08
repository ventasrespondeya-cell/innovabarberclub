import os
import json
import datetime
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def obtener_credenciales(scopes):
    if "gcp_service_account" in st.secrets:
        raw_sec = st.secrets["gcp_service_account"]
        # Convertir a diccionario si viene como string JSON
        if isinstance(raw_sec, str):
            creds_dict = json.loads(raw_sec)
        else:
            creds_dict = dict(raw_sec)

        if "private_key" in creds_dict:
            pk = str(creds_dict["private_key"]).strip()
            
            # Remover comillas envueltas accidentales
            if (pk.startswith('"') and pk.endswith('"')) or (pk.startswith("'") and pk.endswith("'")):
                pk = pk[1:-1].strip()
            
            # Normalizar saltos de línea
            pk = pk.replace("\\n", "\n").replace("\r\n", "\n").replace("\r", "\n")
            
            header = "-----BEGIN PRIVATE KEY-----"
            footer = "-----END PRIVATE KEY-----"
            
            if header in pk and footer in pk:
                start = pk.find(header) + len(header)
                end = pk.find(footer)
                cuerpo = pk[start:end].replace(" ", "").replace("\n", "").replace("\t", "").strip()
                # Reconstruir en bloques estrictos de 64 caracteres PEM
                lineas = [cuerpo[i:i+64] for i in range(0, len(cuerpo), 64)]
                pk = f"{header}\n" + "\n".join(lineas) + f"\n{footer}\n"
            
            creds_dict["private_key"] = pk

        return Credentials.from_service_account_info(creds_dict, scopes=scopes)
    elif os.path.exists("credentials.json"):
        return Credentials.from_service_account_file("credentials.json", scopes=scopes)
    else:
        raise FileNotFoundError("No se encontraron credenciales en Secrets ni en credentials.json")

class GoogleCalendarManager:
    def __init__(self, credentials_path="credentials.json"):
        self.scopes = ["https://www.googleapis.com/auth/calendar"]
        self.creds = obtener_credenciales(self.scopes)
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
