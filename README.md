# Projeto Final: Arquitetura Serverless, Event-Driven e IA (Vertex AI)

Este repositório apresenta a consolidação final da disciplina de **Serverless Computing e Arquiteturas Event-Driven**. A solução proposta não é apenas um conjunto de funções, mas um ecossistema resiliente, seguro e inteligente que integra automação DevOps com IA Generativa.

---

## 🏗️ Arquitetura e Fluxo de Dados

A arquitetura foi desenhada para equilibrar rigor processual com agilidade de resposta. Ela se divide em dois domínios principais:

1.  **Domínio de Negócio (Orquestração):** Processamento de pedidos via Cloud Workflows.
2.  **Domínio de Operações (Coreografia):** Triagem inteligente de falhas via Pub/Sub e Vertex AI.

---

## 🧠 Justificativa das Decisões Arquiteturais

Abaixo, detalho o **porquê** de cada escolha técnica, conforme os critérios de avaliação de maturidade arquitetural.

### 1. Orquestração no Fluxo de Pedidos (Aula 3)
*   **Decisão:** Uso de **Google Cloud Workflows**.
*   **Justificativa:** Em processos que envolvem transações financeiras (Charge) e reserva de recursos (Reserve), a consistência é vital. A orquestração permite gerenciar retentativas, lidar com estados de erro de forma centralizada e garantir que o microsserviço de "Envio" (Ship) só seja chamado se os passos anteriores tiverem sucesso.
*   **Alternativa Considerada:** Coreografia pura (Pub/Sub entre cada etapa).
*   **Por que foi descartada?** A coreografia tornaria o rastreamento do estado do pedido muito complexo, dificultando a implementação de compensações (Sagas) caso um pagamento falhasse após a reserva.

### 2. Coreografia no Agente de Triagem de IA (Aula 2 e 6)
*   **Decisão:** Agente de IA como assinante assíncrono via **Pub/Sub**.
*   **Justificativa:** A triagem de um erro de build não deve impedir a conclusão do build ou do deploy. Ao usar eventos, o sistema de CI/CD apenas notifica a falha. O Agente de IA, agindo de forma desacoplada, consome essa falha, investiga e loga a solução sem adicionar latência ao pipeline principal.
*   **Alternativa Considerada:** Chamada síncrona de IA dentro do pipeline de Build.
*   **Por que foi descartada?** Aumentaria o tempo de build e criaria uma dependência crítica (o build falharia se a API da Vertex AI estivesse indisponível).

### 3. IA com Function Calling e Padrão ReAct (Aula 6)
*   **Decisão:** Uso do Gemini 1.5 Flash com **Function Calling**.
*   **Justificativa:** IA generativa pura pode "alucinar" sobre erros. Ao fornecer a ferramenta `get_build_logs`, forçamos o modelo a basear seu raciocínio (Reason) em dados reais (Act/Observe). Isso transforma a IA de um chat passivo em um agente operacional.
*   **Alternativa Considerada:** Enviar todos os logs no prompt inicial.
*   **Por que foi descartada?** Ineficiência de tokens e custo. O Function Calling permite que a IA decida qual trecho de log é relevante.

### 4. Observabilidade Estruturada (Aula 4)
*   **Decisão:** Uso de **Logging Estruturado (JSON)** e correlação de **Trace Context**.
*   **Justificativa:** A observabilidade aqui é o "alimento" da IA. Sem logs estruturados, a IA teria dificuldade em parsear erros. Com JSON, ela identifica campos como `build_id` e `severity` instantaneamente, permitindo diagnósticos precisos.

### 5. Segurança por Isolamento (Aula 5)
*   **Decisão:** Identidades isoladas (**Service Accounts**) e **Secret Manager**.
*   **Justificativa:** O Agente de IA tem permissão apenas para `aiplatform.user` e `logging.viewer`. Seguimos o **Princípio do Menor Privilégio**: ele pode investigar erros, mas não tem acesso ao banco de dados de clientes ou chaves financeiras.

---

## 🚀 Resumo Executivo para Avaliação
Esta arquitetura prova que sistemas serverless modernos devem ser híbridos: **Orquestrados** onde o controle é mandatório e **Coreografados** onde a agilidade e o desacoplamento são essenciais. A integração da IA Vertex AI fecha o ciclo, transformando a observabilidade passiva em uma força de auto-cura e triagem proativa.

---
**Matheus Bravo da Silva**
*Repositório completo, CI/CD operacional e documentação técnica validada.*
