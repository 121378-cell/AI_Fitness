import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from google.generativeai import Client
from datetime import date, timedelta
import json

# -------------------------------
# Configurar Gem
gem = Client(api_key=os.getenv("GEMINI_API_KEY"))

# -------------------------------
# 1️⃣ Leer CSV Garmin
CSV_FILE = r"data/garmin_stats.csv"  # mover tu CSV de C:/Reports cuando termine la descarga
df_garmin = pd.read_csv(CSV_FILE)
today = date.today().isoformat()

# Resumen diario
today_garmin = df_garmin[df_garmin['date'] == today]
cardio_summary = ""
if not today_garmin.empty:
    metrics = today_garmin.iloc[0]
    cardio_summary = (
        f"Cardio y métricas fisiológicas del día:\n"
        f"- HRV: {metrics.get('hrv','N/A')}\n"
        f"- Sueño: {metrics.get('sleep_hours','N/A')}\n"
        f"- Pasos: {metrics.get('steps','N/A')}\n"
        f"- Calorías: {metrics.get('calories','N/A')}\n"
    )
else:
    cardio_summary = "No hay datos de Garmin para hoy.\n"

# Resumen semanal (últimos 7 días)
week_ago = (pd.to_datetime(today) - timedelta(days=7)).date()
df_week = df_garmin[pd.to_datetime(df_garmin['date']).dt.date >= week_ago]
week_summary = f"Resumen semanal: {len(df_week)} días registrados.\n"

# -------------------------------
# 2️⃣ Leer Google Sheet (fuerza)
SERVICE_ACCOUNT_FILE = r"service_account.json"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gc = gspread.authorize(creds)

SHEET_NAME = 'Fuerza Diario'  # Ajusta al nombre de tu sheet
worksheet = gc.open(SHEET_NAME).sheet1
records = worksheet.get_all_records()
df_fuerza = pd.DataFrame(records)

fuerza_summary = "Ejercicios de fuerza:\n"
for i, row in df_fuerza.iterrows():
    fuerza_summary += f"- {row['Ejercicio']}: {row['Series']}x{row['Reps']} a {row.get('Peso','N/A')}kg\n"

# -------------------------------
# 3️⃣ Crear prompt para la Gem
prompt = f"""
Resumen diario:

{cardio_summary}

{fuerza_summary}

Resumen semanal:

{week_summary}

Sugiere un plan de entrenamiento diario óptimo considerando recuperación, intensidad y balance entre cardio y fuerza.
"""

# -------------------------------
# 4️⃣ Generar entrenamiento con Gem
response = gem.generate_text(prompt=prompt)

# -------------------------------
# 5️⃣ Mostrar resultado
print("=== ENTRENAMIENTO DIARIO RECOMENDADO ===")
print(response.text)

# -------------------------------
# 6️⃣ Guardar plan diario
output_file = os.path.join("output", f"plan_{today}.json")
os.makedirs("output", exist_ok=True)
with open(output_file, "w", encoding="utf-8") as f:
    json.dump({"date": today, "plan": response.text}, f, indent=2, ensure_ascii=False)

print(f"\nPlan guardado en: {output_file}")