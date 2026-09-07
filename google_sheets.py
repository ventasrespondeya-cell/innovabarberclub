import os
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

class GoogleSheetsManager:
    def __init__(self, credentials_path="credentials.json"):
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        
        # 1. Intentar cargar desde los Secrets de Streamlit Cloud
        if "gcp_service_account" in st.secrets:
            self.creds = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], 
                scopes=self.scopes
            )
        # 2. Si no está en la nube, cargar desde el archivo local credentials.json
        elif os.path.exists(credentials_path):
            self.creds = Credentials.from_service_account_file(
                credentials_path, 
                scopes=self.scopes
            )
        else:
            raise FileNotFoundError("No se encontraron credenciales válidas en Secrets ni en credentials.json")

        self.service = build("sheets", "v4", credentials=self.creds)

    def agregar_reserva(self, spreadsheet_id, datos):
        """
        Agrega una nueva fila de datos a la hoja.
        datos: Lista con [Fecha, Hora, Nombre, Email, Servicio, Notas]
        """
        range_name = "'Hoja 1'!A:F"
        
        body = {
            "values": [datos]
        }
        
        request = self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body
        )
        
        response = request.execute()
        return response