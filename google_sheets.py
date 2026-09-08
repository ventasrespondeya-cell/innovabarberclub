import os
import json
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def obtener_credenciales(scopes):
    if "gcp_service_account" in st.secrets:
        raw_sec = st.secrets["gcp_service_account"]
        if isinstance(raw_sec, str):
            creds_dict = json.loads(raw_sec)
        else:
            creds_dict = dict(raw_sec)

        if "private_key" in creds_dict:
            pk = str(creds_dict["private_key"]).strip()
            
            if (pk.startswith('"') and pk.endswith('"')) or (pk.startswith("'") and pk.endswith("'")):
                pk = pk[1:-1].strip()
            
            pk = pk.replace("\\n", "\n").replace("\r\n", "\n").replace("\r", "\n")
            
            header = "-----BEGIN PRIVATE KEY-----"
            footer = "-----END PRIVATE KEY-----"
            
            if header in pk and footer in pk:
                start = pk.find(header) + len(header)
                end = pk.find(footer)
                cuerpo = pk[start:end].replace(" ", "").replace("\n", "").replace("\t", "").strip()
                lineas = [cuerpo[i:i+64] for i in range(0, len(cuerpo), 64)]
                pk = f"{header}\n" + "\n".join(lineas) + f"\n{footer}\n"
            
            creds_dict["private_key"] = pk

        return Credentials.from_service_account_info(creds_dict, scopes=scopes)
    elif os.path.exists("credentials.json"):
        return Credentials.from_service_account_file("credentials.json", scopes=scopes)
    else:
        raise FileNotFoundError("No se encontraron credenciales en Secrets ni en credentials.json")

class GoogleSheetsManager:
    def __init__(self, credentials_path="credentials.json"):
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        self.creds = obtener_credenciales(scopes)
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
