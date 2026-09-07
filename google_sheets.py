import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

class GoogleSheetsManager:
    def __init__(self, credentials_path="credentials.json"):
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"No se encontró el archivo {credentials_path}")
            
        self.creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
        self.service = build("sheets", "v4", credentials=self.creds)

    def agregar_reserva(self, spreadsheet_id, datos):
        """
        Agrega una nueva fila de datos a la hoja.
        datos: Lista con [Fecha, Hora, Nombre, Email, Servicio, Notas]
        """
        # Se especifica el nombre exacto de la pestaña
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