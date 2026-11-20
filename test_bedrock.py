"""Prueba rápida de conexión con Amazon Bedrock (sin interfaz).

Uso: python test_bedrock.py
"""

import os

import boto3
from dotenv import load_dotenv

from system_prompt import build_system_prompt

load_dotenv()
REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")

if not os.getenv("AWS_BEARER_TOKEN_BEDROCK"):
    raise SystemExit("Falta AWS_BEARER_TOKEN_BEDROCK en el archivo .env")

print(f"Región: {REGION}\nModelo: {MODEL_ID}\n")

try:
    client = boto3.client("bedrock-runtime", region_name=REGION)
    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": build_system_prompt("Tutor de conceptos")}],
        messages=[{"role": "user", "content": [{"text": "¿Qué es RAG en una frase?"}]}],
        inferenceConfig={"temperature": 0.4, "maxTokens": 200},
    )
    print("Conexión exitosa. Respuesta del modelo:\n")
    print(response["output"]["message"]["content"][0]["text"])
except Exception as e:
    print(f"Error al conectar con Bedrock:\n{e}")
