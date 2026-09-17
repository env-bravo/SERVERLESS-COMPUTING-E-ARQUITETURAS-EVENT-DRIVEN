# Guia de Segurança e IAM - Aula 5

Este documento detalha os comandos necessários para configurar o ambiente de acordo com o **Princípio do Menor Privilégio** e o uso de **Custom Roles** com **Secret Manager**.

## 1. Criação das Service Accounts (SAs)

Cada etapa do processo de pedido terá sua própria identidade:

```bash
# SA para Reserva de Estoque
gcloud iam service-accounts create sa-order-reserve \
    --display-name="SA para Reserva de Estoque"

# SA para Pagamento
gcloud iam service-accounts create sa-order-charge \
    --display-name="SA para Pagamento"

# SA para Envio
gcloud iam service-accounts create sa-order-ship \
    --display-name="SA para Envio"
```

## 2. Permissões Básicas (Firestore)

Todas as SAs precisam gravar o status do pedido no Firestore.

```bash
PROJECT_ID=$(gcloud config get-value project)

for SA in sa-order-reserve sa-order-charge sa-order-ship; do
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/datastore.user"
done
```

## 3. Configuração do Secret Manager e Custom Role

### A. Criar o Segredo
```bash
# Substitua 'SUA_CHAVE_STRIPE' pela chave real
echo -n "sk_test_..." | \
    gcloud secrets create stripe-api-key \
    --data-file=- \
    --replication-policy="automatic"
```

### B. Criar Custom Role para Acesso ao Segredo
Criamos uma role que permite apenas ler versões de segredos, sem permissões de edição ou listagem global.

```bash
gcloud iam roles create PaymentSecretAccessor \
    --project=${PROJECT_ID} \
    --title="Payment Secret Accessor" \
    --description="Permite apenas o acesso e leitura de versões de segredos." \
    --permissions="secretmanager.versions.get,secretmanager.versions.access" \
    --stage="GA"
```

### C. Vínculo no Nível do Recurso (Menor Privilégio)
Apenas a conta de **Pagamento** terá acesso ao segredo do **Stripe**. As outras contas (Estoque/Envio) serão bloqueadas se tentarem acessá-lo.

```bash
gcloud secrets add-iam-policy-binding stripe-api-key \
    --member="serviceAccount:sa-order-charge@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="projects/${PROJECT_ID}/roles/PaymentSecretAccessor"
```

## 4. Workload Identity e Cloud Build
Para que o Cloud Build possa fazer o deploy usando as SAs criadas, ele precisa da permissão `iam.serviceAccountUser`.

```bash
CB_SA=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")@cloudbuild.gserviceaccount.com

for SA in sa-order-reserve sa-order-charge sa-order-ship; do
    gcloud iam service-accounts add-iam-policy-binding \
        ${SA}@${PROJECT_ID}.iam.gserviceaccount.com \
        --member="serviceAccount:${CB_SA}" \
        --role="roles/iam.serviceAccountUser"
done
```
