import os

import boto3
import streamlit as st
from dotenv import load_dotenv

from system_prompt import PROFILES, build_system_prompt

# 1. Configuración. boto3 (>= 1.39) toma la API key de Bedrock de la variable
#    AWS_BEARER_TOKEN_BEDROCK automáticamente;
load_dotenv()
REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
# Mensajes del historial que se envían al modelo. Es impar para que el recorte
# siempre empiece con un mensaje del usuario, como exige la Converse API.
MAX_HISTORY = 21

st.set_page_config(page_title="RAGtutor - AWS AI Practitioner", layout="centered")


@st.cache_resource
def get_client():
    return boto3.client("bedrock-runtime", region_name=REGION)


def reset_chat():
    st.session_state.messages = []


# 2. Barra lateral: perfil del experto y estado de la conexión
with st.sidebar:
    st.header("Configuración")
    profile = st.selectbox("Perfil del experto", list(PROFILES), on_change=reset_chat)
    st.caption("Cambiar de perfil inicia una conversación nueva.")
    st.button("Nueva conversación", on_click=reset_chat)
    st.divider()
    if os.getenv("AWS_BEARER_TOKEN_BEDROCK"):
        st.success("API key de Bedrock cargada")
    else:
        st.error("Falta AWS_BEARER_TOKEN_BEDROCK en el archivo .env")
    st.caption(f"Región: {REGION}  \nModelo: {MODEL_ID}")

st.title("RAGtutor")
st.caption(f"Asistente de RAG y LLMs para AWS AI Practitioner · {profile}")

# 3. Historial de la conversación (se guarda en la sesión de Streamlit)
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"][0]["text"])


def stream_response(messages):
    """Llama a Bedrock con la Converse API y devuelve el texto a medida que llega."""
    response = get_client().converse_stream(
        modelId=MODEL_ID,
        system=[{"text": build_system_prompt(profile)}],
        messages=messages,
        inferenceConfig={"temperature": PROFILES[profile]["temperature"], "maxTokens": 1024},
    )
    for event in response["stream"]:
        if "contentBlockDelta" in event:
            yield event["contentBlockDelta"]["delta"].get("text", "")


# 4. Nueva pregunta del usuario
if prompt := st.chat_input("Pregunta sobre RAG, LLMs o Amazon Bedrock..."):
    st.session_state.messages.append({"role": "user", "content": [{"text": prompt}]})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            answer = st.write_stream(stream_response(st.session_state.messages[-MAX_HISTORY:]))
            st.session_state.messages.append({"role": "assistant", "content": [{"text": answer}]})
        except Exception as e:
            st.session_state.messages.pop()  # para poder reintentar la misma pregunta
            if "UnrecognizedClient" in str(e) or "AccessDenied" in str(e):
                st.error("La API key no es válida, expiró o no tiene acceso al modelo. "
                         "Genera una nueva, actualiza el .env y reinicia la app.")
            else:
                st.error(f"Error al comunicarse con Bedrock: {e}")
