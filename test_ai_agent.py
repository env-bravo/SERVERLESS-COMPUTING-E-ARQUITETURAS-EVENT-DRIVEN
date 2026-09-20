import os
import json
import base64
from google.cloud import pubsub_v1

PROJECT_ID = "project-4a227026-caa6-4ceb-928"
TOPIC_NAME = "build-failures"

def trigger_ai_triage(build_id, error_type="IAM_PERMISSION"):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)
    
    # Payload simulando uma falha de build
    data = {
        "build_id": build_id,
        "status": "FAILURE",
        "error_detail": error_type
    }
    
    message_json = json.dumps(data)
    message_bytes = message_json.encode("utf-8")
    
    print(f"Enviando evento de falha para o build: {build_id}...")
    future = publisher.publish(topic_path, data=message_bytes)
    print(f"Mensagem ID: {future.result()}")

if __name__ == "__main__":
    # Teste 1: Falha de Permissão (IAM)
    trigger_ai_triage("build-test-999", error_type="403 Permission Denied")
