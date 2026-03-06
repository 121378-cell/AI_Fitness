import gspread
from google.oauth2.service_account import Credentials

# Archivo de credenciales
SERVICE_ACCOUNT_FILE = "service_account.json"

# Permisos
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Autenticación
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

client = gspread.authorize(creds)

# Nombre de tu Google Sheet
SHEET_NAME = "Fuerza Diario"

sheet = client.open(SHEET_NAME).sheet1

data = sheet.get_all_records()

print("Datos encontrados:")
for row in data[:5]:
    print(row)