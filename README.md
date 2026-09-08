# Aula 4 - Observabilidade e Performance
## Repositório: SERVERLESS-COMPUTING-E-ARQUITETURAS-EVENT-DRIVEN

Este repositório contém a implementação do Checkpoint 4, focado em instrumentação, monitoramento e otimização de um pipeline de pedidos serverless.

---

### 1. Implementação de Observabilidade

#### Cloud Logging (Estruturado)
O pipeline foi instrumentado para emitir logs em formato JSON (`jsonPayload`), facilitando a análise e filtragem.
- **Trace ID Correlation:** Implementada a extração e propagação do header `X-Cloud-Trace-Context` para correlacionar logs de diferentes serviços no **Cloud Trace**.
- **Severidade:** Uso correto de níveis `INFO` para fluxo normal e `ERROR` para falhas.

#### Cloud Monitoring (Métricas de Experiência)
Foram configuradas métricas que refletem a jornada real do produto, migradas para **Log-based Metrics** para maior eficiência:
- `logging.googleapis.com/user/stock_reserved`: Sucesso na reserva de estoque.
- `logging.googleapis.com/user/payment_status_success`: Conversão de vendas.
- `logging.googleapis.com/user/payment_status_failures`: Perda de receita/falhas técnicas.
- `logging.googleapis.com/user/order_shipped`: Conclusão do pipeline.

#### Alerting Policy
Configurada uma política de alerta crítica (`payment_alert_policy.json`) baseada na métrica de falha de pagamento:
- **Condição:** Dispara se houver mais de 2 falhas em um intervalo de 5 minutos.
- **Foco:** Reduzir o ruído de alertas (alert fatigue) focando no que impacta o negócio.

---

### 2. Otimizações de Performance e Custo

Foram aplicadas/propostas as seguintes otimizações concretas:

| Otimização | Justificativa Técnica | Impacto |
| :--- | :--- | :--- |
| **Migração para Log-based Metrics** | Substituição do SDK de Monitoring por logs assíncronos. | **Performance:** Redução de 100-300ms de latência por passo. **Custo:** Menor tempo de execução e imagem menor. |
| **Startup CPU Boost** | Alocação extra de CPU durante o boot da função (Cold Start). | **Cold Start:** Redução da latência inicial de ~6s para <2s em funções Python. |
| **Lazy Initialization (Singleton)** | Inicialização de clientes GCP (Firestore/Logging) apenas quando demandados. | **Recursos:** Menor pegada de memória e maior estabilidade na escalabilidade. |

---

### 3. Como Visualizar os Resultados

1. **Trace:** Acesse o console do **Cloud Trace** para visualizar a latência ponta a ponta e identificar gargalos (Ex: o passo de `charge` domina a latência).
2. **Logs:** No **Logs Explorer**, utilize o filtro `jsonPayload.metric_event:*` para ver os eventos de negócio.
3. **Alertas:** Verifique em **Monitoring > Alerting** a política ativa "Alerta Crítico: Taxa de Falha em Pagamentos".

---
**Matheus Bravo da Silva** - bravo.htk@gmail.com
