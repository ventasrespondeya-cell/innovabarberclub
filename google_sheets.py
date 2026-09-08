import os
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def reconstruir_llave_pem(key: str) -> str:
    """
    Destruye el formato defectuoso y reconstruye la llave privada 
    asegurando el formato PEM perfecto (64 caracteres por línea).
    """
    if not key:
        return key
        
    header = "-----BEGIN PRIVATE KEY-----"
    footer = "-----END PRIVATE KEY-----"
    
    # Unificar todo a una sola línea eliminando cualquier tipo de salto
    key_plana = str(key).replace("\\\\n", " ").replace("\\n", " ").replace("\n", " ")
    
    if header in key_plana and footer in key_plana:
        # Extraer estrictamente el cuerpo en Base64
        cuerpo = key_plana.split(header)[1].split(footer)[0]
        # Pulverizar cualquier espacio en blanco, tabulación o basura
        cuerpo = cuerpo.replace(" ", "").replace("\t", "").replace("\"", "").replace("'", "")
        
        # Formatear el cuerpo a exactamente 64 caracteres por línea (Estándar PEM estricto)
        lineas = [cuerpo[i:i+64] for i in range(0, len(cuerpo), 64)]
        
        # Ensamblar la llave final
        return f"{header}\n" + "\n".join(lineas) + f"\n{footer}\n"
        
    return key

class GoogleSheetsManager:
    def __init__(self, credentials_path="credentials.json"):
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            if "private_key" in creds_dict:
                creds_dict["private_key"] = reconstruir_llave_pem(creds_dict["private_key"])
                
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