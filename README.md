# RAGtutor: Asistente de RAG y LLMs con Amazon Bedrock

Asistente conversacional para preparar la certificación **AWS Certified AI Practitioner (AIF-C01)** en el tema **RAG (Retrieval-Augmented Generation) y uso de LLMs**. Está hecho con Streamlit y usa un modelo fundacional de Amazon Bedrock a través de la Converse API.

Ejercicio práctico *LLM Bedrock* del semillero AWS. Modalidad individual. Santiago Jaimes.

## 1. Qué hace

- Chat que muestra la respuesta a medida que el modelo la genera.
- Tres perfiles de experto, que se eligen en la barra lateral:
  - **Tutor de conceptos:** explica con una analogía, el detalle técnico y cómo se ve en AWS.
  - **Examinador AIF-C01:** hace preguntas tipo examen (A-D) y explica la respuesta.
  - **Arquitecto de soluciones:** diseña arquitecturas RAG en AWS para un caso de uso.
- Guarda el historial de la conversación en la sesión y lo envía al modelo para mantener el contexto.
- Se autentica con una **API key de Amazon Bedrock**, leída desde un archivo `.env` que no se sube a Git.

## 2. Tecnologías

Python, Streamlit, Amazon Bedrock (Converse API), boto3, python-dotenv y Docker.

## 3. Estructura

```
s2026-q4_c-llmbedrock-santiagojaimes/
├── app.py              # Interfaz de chat en Streamlit y llamada a Bedrock
├── system_prompt.py    # Prompt base y los tres perfiles de experto
├── test_bedrock.py     # Prueba de conexión con Bedrock desde la terminal
├── requirements.txt    # Dependencias de Python
├── Dockerfile          # Imagen para ejecutar la app en un contenedor
├── .env                # Plantilla de configuración (sin credenciales)
├── .gitignore          # Excluye .env y archivos temporales de Git
└── .dockerignore       # Excluye .env y archivos temporales de la imagen
```

## 4. Diseño del prompt

El prompt de sistema tiene dos partes (ver `system_prompt.py`):

1. **Base común:** quién es el asistente, qué temas cubre y sus reglas (responder en español, no inventar servicios de AWS, decir cuando no está seguro, volver al tema si le preguntan otra cosa y no revelar sus instrucciones).
2. **Perfil:** cambia el rol, el formato de respuesta y la temperature. El tutor usa 0.4 para dar definiciones consistentes. El examinador usa 0.7 para variar las preguntas. El arquitecto usa 0.5.

## 5. Cómo ejecutarlo

### Paso 1. Requisitos

- Una cuenta de AWS con acceso a Amazon Bedrock.
- Docker, o Python 3.10 o superior.

### Paso 2. Habilitar el modelo

En la consola de AWS, en la región `us-east-1`, abre **Amazon Bedrock > Model access** y confirma que tienes acceso a **Claude Haiku 4.5**.

### Paso 3. Generar la API key

En **Amazon Bedrock > API keys** (misma región) genera una clave de corto plazo y cópiala. Dura como máximo 12 horas.

### Paso 4. Crear el archivo `.env`


Ábrelo y pega la clave:

```
AWS_BEARER_TOKEN_BEDROCK=tu_api_key
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-haiku-4-5-20251001-v1:0
```

### Paso 5A. Ejecutar con Docker

```bash
docker build -t ragtutor .
docker run --rm -p 8501:8501 --env-file .env ragtutor
```

### Paso 5B. Ejecutar con Python

```bash
python -m venv venv
source venv/bin/activate             # macOS / Linux
venv\Scripts\activate                # Windows

pip install -r requirements.txt
python test_bedrock.py               # opcional: prueba la conexión
streamlit run app.py
```

### Paso 6. Usar la app

Abre <http://localhost:8501>, elige un perfil en la barra lateral y escribe tu pregunta.

## 6. Problemas frecuentes

| Mensaje | Solución |
|---|---|
| "Falta AWS_BEARER_TOKEN_BEDROCK" | Crea el `.env` (paso 4) y reinicia la app. |
| "La API key no es válida, expiró o no tiene acceso al modelo" | Genera una nueva clave (paso 3) o revisa el acceso al modelo (paso 2). |
| `Unable to locate credentials` | Actualiza boto3: `pip install --upgrade boto3` (se necesita la versión 1.39 o superior). |
| `ValidationException` | Revisa que `BEDROCK_MODEL_ID` esté habilitado en la región de `AWS_REGION`. |

## 7. Seguridad

- El archivo `.env` está en `.gitignore` y en `.dockerignore`: no se sube al repositorio ni queda dentro de la imagen.
- La clave se entrega al contenedor solo al ejecutarlo, con `--env-file .env`.
