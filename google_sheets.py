import os
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def limpiar_llave_privada(key: str) -> str:
    if not key:
        return key
    key = str(key).strip()
    if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
        key = key[1:-1]
    return key.replace("\\n", "\n").strip()

class GoogleSheetsManager:
    def __init__(self, credentials_path="credentials.json"):
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            if "private_key" in creds_dict:
                creds_dict["private_key"] = limpiar_llave_privada(creds_dict["private_key"])
                
            self.creds = Credentials.from_service_account_info(
                creds_dict, 
                scopes=scopes
            )
        elif os.path.exists(credentials_path):
            self.creds = Credentials.from_service_account_file(
                credentials_path, 
                scopes=scopes
            )
        else:
            raise FileNotFoundError("No se encontraron credenciales válidas en Secrets ni en credentials.json")

        self.service = build("sheets", "v4", credentials=self.creds)

    def agregar_reserva(self, spreadsheet_id, datos):
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
