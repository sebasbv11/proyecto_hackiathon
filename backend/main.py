import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SUPABASE
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# OPENAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# MODELO REQUEST
class EmergencyRequest(BaseModel):
    nombre: str
    cedula: str
    poliza: str
    motivo: str


# ROOT
@app.get("/")
def root():
    return {
        "message": "Emergency AI Agent Running"
    }


# HISTORIAL
@app.get("/cases")
def get_cases():

    response = supabase.table("emergency_cases") \
        .select("*") \
        .order("id", desc=True) \
        .execute()

    return response.data


# WEBHOOK PRINCIPAL
@app.post("/emergency")
def analyze_emergency(data: EmergencyRequest):

    # Buscar póliza
    policy = supabase.table("policies") \
        .select("*") \
        .eq("policy_number", data.poliza) \
        .execute()

    if not policy.data:
        return {
            "status": "error",
            "message": "Póliza no encontrada"
        }

    policy_info = policy.data[0]

    # Buscar preexistencias
    conditions = supabase.table("preexisting_conditions") \
        .select("*") \
        .eq("patient_cedula", data.cedula) \
        .execute()

    preexisting = [
        c["condition"]
        for c in conditions.data
    ]

    # PROMPT IA
    prompt = f"""
    Analiza el siguiente ingreso hospitalario.

    Paciente: {data.nombre}
    Motivo de emergencia: {data.motivo}
    Preexistencias: {preexisting}
    Cobertura: {policy_info['coverage']}

    Genera:
    1. Resumen breve
    2. Nivel de riesgo
    3. Recomendación rápida
    """

    # OPENAI
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    ai_summary = response.choices[0].message.content

    # ENVIAR ALERTA A N8N
    requests.post(
        "http://localhost:5678/webhook/alertas-emergencias",
        json={
            "patient": data.nombre,
            "policy": data.poliza,
            "status": policy_info["status"],
            "summary": ai_summary
        }
    )

    # GUARDAR CASO
    supabase.table("emergency_cases").insert({
        "patient_name": data.nombre,
        "policy_number": data.poliza,
        "coverage_status": policy_info["status"],
        "risk_level": "Moderado",
        "ai_summary": ai_summary,
        "notifications_sent": True
    }).execute()

    # RESPUESTA FINAL
    return {
        "policy_status": policy_info["status"],
        "coverage": policy_info["coverage"],
        "copay": policy_info["copay"],
        "preexisting_conditions": preexisting,
        "ai_summary": ai_summary,
        "notifications": [
            "Admisiones notificadas",
            "Gestor del seguro notificado"
        ]
    }