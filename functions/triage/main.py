import os
import base64
import json
import functions_framework
from google.cloud import logging as cloud_logging
from vertexai.generative_models import (
    GenerativeModel,
    FunctionDeclaration,
    Tool,
    Part,
    Content
)
import vertexai

# Configuração de Logging Estruturado (Aula 4)
log_client = cloud_logging.Client()
logger = log_client.logger("triage-agent")

def log_structured(message, severity="INFO", **kwargs):
    entry = {"message": message, **kwargs}
    logger.log_struct(entry, severity=severity)

# Inicialização Vertex AI (Aula 6)
PROJECT_ID = os.environ.get("GCP_PROJECT")
# Usamos a região onde a função está rodando para buscar o modelo (us-central1 é a mais estável)
LOCATION = os.environ.get("FUNCTION_REGION", "us-central1")
vertexai.init(project=PROJECT_ID, location=LOCATION)

# --- DEFINIÇÃO DE FERRAMENTAS (Function Calling) ---

# Declaração da função que o Gemini poderá "chamar"
get_build_logs_decl = FunctionDeclaration(
    name="get_build_logs",
    description="Retorna os logs de um build que falhou no Cloud Build para diagnóstico.",
    parameters={
        "type": "object",
        "properties": {
            "build_id": {"type": "string", "description": "O ID único do build no Cloud Build."}
        },
        "required": ["build_id"]
    },
)

# Tool que agrupa as declarações
triage_tool = Tool(
    function_declarations=[get_build_logs_decl],
)

# --- LÓGICA DO AGENTE ---

def mock_get_build_logs(build_id):
    """Simula a busca de logs. No projeto real, usaria a API do Cloud Build."""
    log_structured(f"IA solicitou logs do build {build_id}", severity="DEBUG")
    # Simula um erro comum de falta de permissão no Firestore que corrigimos na Aula 5
    return "ERROR: google.api_core.exceptions.PermissionDenied: 403 Missing permissions for firestore.databases.get"

@functions_framework.cloud_event
def triage_build_failure(cloud_event):
    """Gatilho Pub/Sub (Aula 2) para triagem de falhas."""
    
    # Decodificação do Evento (Aula 2)
    try:
        data = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
        payload = json.loads(data)
        build_id = payload.get("build_id", "unknown")
    except Exception as e:
        log_structured("Falha ao decodificar evento Pub/Sub", severity="ERROR", error=str(e))
        return

    log_structured(f"Iniciando triagem para o build {build_id}", severity="INFO", build_id=build_id)

    # Configuração do Modelo (Aula 6)
    # Usamos o alias gemini-1.5-flash para maior compatibilidade regional
    model = GenerativeModel(
        "gemini-1.5-flash",
        tools=[triage_tool],
        system_instruction=(
            "Você é um Agente de Triagem DevOps especializado em Google Cloud. "
            "Ao receber um ID de build, use a ferramenta 'get_build_logs' para investigar a falha. "
            "Analise se o erro é de permissão (IAM), código ou infraestrutura. "
            "Seja conciso e sugira uma ação corretiva baseada no Princípio do Menor Privilégio."
        )
    )

    # Início do Loop ReAct (Reason + Act)
    chat = model.start_chat()
    
    # Pergunta inicial da IA
    prompt = f"O build {build_id} falhou. Investigue a causa e me dê um resumo."
    
    try:
        response = chat.send_message(prompt)

        # Verifica se a IA quer chamar uma função
        parts = response.candidates[0].content.parts
        if parts and parts[0].function_call:
            function_call = parts[0].function_call
            if function_call.name == "get_build_logs":
                # Executa a ação (Act) no nosso código
                logs = mock_get_build_logs(function_call.args["build_id"])
                
                # Devolve a observação (Observe) para a IA
                response = chat.send_message(
                    Part.from_function_response(
                        name="get_build_logs",
                        response={"content": logs}
                    )
                )

        # Resultado Final da Investigação
        final_analysis = response.text
        log_structured(
            "Triagem concluída pela IA", 
            severity="INFO", 
            analysis=final_analysis, 
            build_id=build_id
        )
        
        return final_analysis

    except Exception as e:
        log_structured("Erro ao processar raciocínio da IA", severity="ERROR", error=str(e))
        return f"Erro de IA: {str(e)}"
