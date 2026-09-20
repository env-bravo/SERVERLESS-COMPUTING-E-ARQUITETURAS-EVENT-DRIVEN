#!/bin/bash

# Configurações iniciais
PROJECT_ID="project-4a227026-caa6-4ceb-928"
REGION="us-central1"
SA_NAME="sa-triage-agent"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
TOPIC_NAME="build-failures"

echo "------------------------------------------------------------"
echo "Iniciando Setup de Segurança e Infra para o Agente de IA..."
echo "Projeto: ${PROJECT_ID}"
echo "------------------------------------------------------------"

# 1. Ativar APIs Necessárias
echo "[1/4] Ativando APIs (Vertex AI, Cloud Build, Pub/Sub)..."
gcloud services enable aiplatform.googleapis.com \
                       cloudbuild.googleapis.com \
                       pubsub.googleapis.com \
                       run.googleapis.com \
                       cloudfunctions.googleapis.com \
                       --project=${PROJECT_ID}

# 2. Criar Tópico Pub/Sub para Falhas de Build
echo "[2/4] Criando tópico Pub/Sub: ${TOPIC_NAME}..."
gcloud pubsub topics create ${TOPIC_NAME} --project=${PROJECT_ID} || echo "Tópico já existe."

# 3. Criar Service Account para o Agente
echo "[3/4] Criando Service Account: ${SA_NAME}..."
gcloud iam service-accounts create ${SA_NAME} \
    --display-name="Service Account para Agente de IA (Triage)" \
    --project=${PROJECT_ID} || echo "Service account já existe."

# 4. Atribuir Permissões (Menor Privilégio - Aula 5)
echo "[4/4] Atribuindo Roles de Segurança..."

# Permissão para usar Vertex AI (Aula 6)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/aiplatform.user"

# Permissão para Logging Estruturado (Aula 4)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/logging.logWriter"

# Permissão para ler logs do Cloud Build (Investigação)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/cloudbuild.builds.viewer"

echo "------------------------------------------------------------"
echo "Setup concluído com sucesso!"
echo "O Agente de IA agora tem permissão para raciocinar e investigar."
echo "------------------------------------------------------------"
