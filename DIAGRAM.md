# Arquitetura do Pipeline de Pedidos

Este projeto utiliza um padrão de **Orquestração de Microsserviços** centralizado, não sendo uma arquitetura orientada a eventos (Event-Driven).

## Diagrama de Interações (Orquestração Síncrona)

```mermaid
sequenceDiagram
    participant User as Usuário/Cliente
    participant Workflow as Cloud Workflows (Orquestrador)
    participant API as API Flask (Cloud Run)
    participant DB as Firestore (Banco de Dados)
    participant PubSub as Pub/Sub (Dead Letter Queue)

    User->>Workflow: Inicia pedido (JSON)
    
    rect rgb(240, 240, 240)
        Note right of Workflow: Step 1: Reservar Estoque
        Workflow->>API: HTTP POST /reserve
        API->>DB: Salva status "RESERVING_STOCK"
        API-->>Workflow: 200 OK (reserved)
    end

    rect rgb(240, 240, 240)
        Note right of Workflow: Step 2: Cobrar Pagamento
        Workflow->>API: HTTP POST /charge (Idempotency-Key)
        
        alt Sucesso no Pagamento
            API->>DB: Atualiza status "PAYMENT_PROCESSED"
            API-->>Workflow: 200 OK (charged)
        else Falha Crítica (após 5 retries)
            Workflow->>PubSub: Publica erro no orders-dlq
            Workflow-->>User: Retorna Erro
        end
    end

    rect rgb(240, 240, 240)
        Note right of Workflow: Step 3: Enviar Pedido
        Workflow->>API: HTTP POST /ship
        API->>DB: Atualiza status "SHIPPING_INITIATED"
        API-->>Workflow: 200 OK (shipped)
    end

    Workflow-->>User: Retorna {"status": "shipped"}
```

## Resumo Técnico e Padrões
- **Padrão Arquitetural**: **Orquestração Centralizada**. O Cloud Workflows detém a inteligência do estado e a ordem das operações.
- **Comunicação**: Predominantemente **Síncrona via HTTP**. O orquestrador aguarda o retorno de cada serviço para prosseguir.
- **Serviços**: Flask App no Cloud Run (Stateless).
- **Persistência**: Firestore para tracking de estados e auditoria.
- **Resiliência**: 
  - Idempotência no pagamento via headers.
  - Retry exponencial (5x) gerenciado pelo orquestrador.
  - **Uso de Mensageria**: Pub/Sub utilizado apenas como **Dead Letter Queue (DLQ)** para tratamento assíncrono de erros fatais, e não para o fluxo principal.
