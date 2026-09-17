# Aula 5 - Segurança e CI/CD
## Repositório: SERVERLESS-COMPUTING-E-ARQUITETURAS-EVENT-DRIVEN

Este repositório contém a implementação da Aula 5, focada no **Princípio do Menor Privilégio**, uso de **Custom Roles**, **Secret Manager** e automação com **Cloud Build**.

---

### 1. Segurança e IAM (Menor Privilégio)

A arquitetura foi refatorada para isolar as responsabilidades e identidades de cada etapa do pipeline:
- **Segregação de Identidades:** O serviço único foi dividido em 3 implantações distintas no Cloud Run (`reserve`, `charge`, `ship`), cada uma com sua própria **Service Account** dedicada.
- **Custom Roles:** Criada a role `PaymentSecretAccessor` com permissões granulares (`versions.access`, `versions.get`), evitando o uso da role predefinida `roles/secretmanager.secretAccessor` que é mais ampla.
- **Vínculo no Nível do Recurso:** A permissão de acesso ao segredo `stripe-api-key` foi concedida **apenas** à Service Account de pagamento e **apenas** para aquele segredo específico.

### 2. Secret Manager

Implementada a gestão de credenciais sensíveis:
- **Centralização:** Removidas chaves fixas ou variáveis de ambiente com valores sensíveis.
- **Integração Nativa:** Uso da funcionalidade nativa do Cloud Run (`--set-secrets`), que injeta o valor do segredo diretamente como variável de ambiente no container.
- **Zero Código Extra:** Removida a necessidade de bibliotecas cliente (`google-cloud-secret-manager`) e lógica de busca manual, tornando a aplicação mais leve e agnóstica à infraestrutura.

### 3. CI/CD com Cloud Build

Automação total do ciclo de vida da aplicação através do arquivo `cloudbuild.yaml`:
1. **Build e Push:** Gera a imagem Docker e envia para o **Artifact Registry**.
2. **Deploy Multi-Serviço:** Faz o deploy automático dos 3 serviços no Cloud Run com suas respectivas configurações de segurança e identidades.
3. **Orquestração Dinâmica:** Atualiza as URLs no arquivo `main.yaml` do **Cloud Workflows** e faz o deploy da versão mais recente da orquestração.

---

### Como Configurar e Executar

1. **Infraestrutura:** Siga os passos detalhados no arquivo `SECURITY.md` para criar as Service Accounts, Roles e Segredos.
2. **Deploy:** Execute o comando abaixo para iniciar o pipeline de CI/CD:
   ```bash
   gcloud builds submit --config cloudbuild.yaml --substitutions=_REPO="seu-repositorio"
   ```
3. **Validação:** 
   - Teste o workflow e verifique nos logs que o passo de pagamento recupera a chave corretamente.
   - Verifique que os outros serviços não possuem acesso ao segredo.

---
**Matheus Bravo da Silva** - bravo.htk@gmail.com
