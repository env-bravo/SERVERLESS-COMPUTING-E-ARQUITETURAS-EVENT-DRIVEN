# Projeto Final: Arquitetura Event-Driven com Agente de IA (Vertex AI)

Este repositório consolida o aprendizado de 6 semanas em **Serverless Computing e Arquiteturas Event-Driven**, culminando em um sistema de processamento de pedidos integrado a um **Agente de Triagem Inteligente** capaz de investigar e diagnosticar falhas de pipeline de forma autônoma.

---

## 🏗️ Arquitetura do Sistema

A solução é composta por três camadas principais que demonstram o equilíbrio entre **Orquestração** e **Coreografia**:

1.  **Orquestração de Pedidos (Cloud Workflows):** Gerencia o fluxo síncrono e transacional de reserva, cobrança e envio.
2.  **Coreografia de IA (Event-Driven / Pub/Sub):** Um Agente de IA (Gemini 1.5 Flash) reage a eventos de falha de build para realizar diagnósticos técnicos.
3.  **Base de Observabilidade e Segurança:** Instrumentação profunda de logs e isolamento de privilégios (IAM).

### Diagrama de Arquitetura
*(Disponível em detalhes em [docs/arch/DIAGRAM.md](docs/arch/DIAGRAM.md))*

---

## 🧠 Decisões Técnicas e Justificativas

### 1. Orquestração vs. Coreografia (Aulas 1, 2 e 3)
*   **Decisão:** Utilizamos **Cloud Workflows** para o pipeline de pedidos.
*   **Por quê?** O processo de pedidos exige controle rigoroso de estado e tratamento de erros sequenciais (ex: não cobrar se não houver reserva). A orquestração centralizada facilita a gestão dessas regras de negócio complexas.
*   **Decisão:** Utilizamos **Pub/Sub** para o acionamento do Agente de IA.
*   **Por quê?** A triagem de falhas é um processo assíncrono e independente. Ao usar coreografia, o pipeline de build não precisa saber quem o está auditando. O Agente de IA é apenas mais um assinante, permitindo escala sem impacto no sistema principal.

### 2. Observabilidade como Input para IA (Aula 4)
*   **Decisão:** Implementação de **Logging Estruturado (JSON)** em todos os microsserviços.
*   **Por quê?** Um agente de IA é tão bom quanto o contexto que ele recebe. O Logging estruturado permite que o Gemini utilize **Function Calling** para filtrar e processar erros específicos, transformando logs brutos em diagnósticos acionáveis.

### 3. IA Generativa com Function Calling (Aula 6)
*   **Decisão:** Uso do padrão **ReAct (Reason + Act)** no Triage Agent.
*   **Por quê?** Em vez de apenas gerar texto, a IA "decide" quando precisa de mais informações (chamando a função `get_build_logs`). Isso reduz alucinações e garante que a análise seja baseada em dados reais do Cloud Build.

### 4. Segurança e Menor Privilégio (Aula 5)
*   **Decisão:** Cada serviço (Reserve, Charge, Ship, Triage Agent) possui sua própria **Service Account** com permissões granulares.
*   **Por quê?** Seguindo o Princípio do Menor Privilégio, garantimos que, se o Agente de IA for comprometido, ele terá acesso apenas à Vertex AI e à leitura de logs, nunca aos dados de pagamento ou chaves de API sensíveis.

---

## 🛠️ Tecnologias Utilizadas
*   **Linguagem:** Python 3.10+ (Flask, Functions Framework)
*   **Infraestrutura:** Google Cloud Run, Cloud Functions (Gen 2), Cloud Workflows.
*   **Mensageria:** Google Cloud Pub/Sub (Choreography layer).
*   **IA:** Vertex AI (Gemini 1.5 Flash).
*   **Segurança:** Secret Manager, IAM Custom Roles.
*   **CI/CD:** Cloud Build.

---

## 🚀 Como Executar
1.  **Setup de Infraestrutura:**
    ```bash
    chmod +x infra/setup_ia_security.sh
    ./infra/setup_ia_security.sh
    ```
2.  **Deploy via Cloud Build:**
    O deploy é automático ao realizar push para a branch `aula-6-projeto-final`.

---

**Matheus Bravo da Silva** - DevOps & Cloud Platform Engineering
Projeto Final para a disciplina de Serverless Computing e Arquiteturas Event-Driven.
