import os
import json
import logging
import time
from flask import Flask, request, jsonify
from google.cloud import firestore
import google.cloud.logging
from google.cloud import monitoring_v3

# Configuração do Logging Estruturado
log_client = google.cloud.logging.Client()
log_client.setup_logging()

# Configuração do Monitoring
monitoring_client = monitoring_v3.MetricServiceClient()
project_name = f"projects/{log_client.project}"

app = Flask(__name__)
db = firestore.Client()

def log_structured(message, severity="INFO", order_id=None, extra=None):
    """Auxiliar para emitir logs estruturados compatíveis com Cloud Logging."""
    trace_header = request.headers.get('X-Cloud-Trace-Context')
    trace_id = None
    if trace_header:
        trace_id = trace_header.split('/')[0]

    log_entry = {
        "message": message,
        "order_id": order_id,
        "severity": severity
    }
    
    if trace_id:
        log_entry["logging.googleapis.com/trace"] = f"projects/{log_client.project}/traces/{trace_id}"
    
    if extra:
        log_entry.update(extra)

    if severity == "ERROR":
        logging.error(json.dumps(log_entry))
    elif severity == "DEBUG":
        logging.debug(json.dumps(log_entry))
    else:
        logging.info(json.dumps(log_entry))

def report_experience_metric(metric_type, value=1, labels=None):
    """Envia uma métrica customizada para o Cloud Monitoring."""
    series = monitoring_v3.TimeSeries()
    series.metric.type = f"custom.googleapis.com/order_experience/{metric_type}"
    
    if labels:
        series.metric.labels.update(labels)
    
    # Define o recurso (Cloud Run no nosso caso)
    series.resource.type = "global" # Usando global para simplificar métricas de negócio
    
    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10**9)
    interval = monitoring_v3.TimeInterval(
        end_time={"seconds": seconds, "nanos": nanos}
    )
    point = monitoring_v3.Point(interval=interval, value={"int64_value": value})
    series.points = [point]

    try:
        monitoring_client.create_time_series(name=project_name, time_series=[series])
    except Exception as e:
        log_structured(f"Erro ao enviar métrica: {str(e)}", severity="DEBUG")

@app.route('/reserve', methods=['POST'])
def reserve():
    data = request.get_json() or {}
    order_id = data.get('order_id', 'unknown')
    
    log_structured("Iniciando reserva de estoque", severity="INFO", order_id=order_id)

    db.collection("order_summaries").document(str(order_id)).set({
        "order_id": order_id,
        "status": "RESERVING_STOCK",
        "updated_at": firestore.SERVER_TIMESTAMP
    }, merge=True)

    # Métrica: Estoque Reservado (Indica sucesso na primeira etapa do desejo do cliente)
    report_experience_metric("stock_reserved", labels={"status": "success"})

    log_structured("Reserva concluída com sucesso", severity="INFO", order_id=order_id, extra={"step": "01"})
    return jsonify({"status": "reserved"}), 200

@app.route('/charge', methods=['POST'])
def charge():
    data = request.get_json() or {}
    order_id = data.get('order_id', 'unknown')

    log_structured("Iniciando processamento de pagamento", severity="INFO", order_id=order_id)

    if order_id == "ORD-FAIL-RETRY":
        log_structured("Simulando falha transiente (503)", severity="ERROR", order_id=order_id)
        # Métrica: Falha no Pagamento (Sinal crítico de perda de receita/experiência)
        report_experience_metric("payment_status", labels={"status": "failure"})
        return "Service Unavailable", 503

    db.collection("order_summaries").document(str(order_id)).update({
        "status": "PAYMENT_PROCESSED",
        "updated_at": firestore.SERVER_TIMESTAMP
    })

    # Métrica: Pagamento Concluído (O sinal mais importante de conversão)
    report_experience_metric("payment_status", labels={"status": "success"})

    log_structured("Pagamento processado com sucesso", severity="INFO", order_id=order_id, extra={"step": "02"})
    return jsonify({"status": "charged"}), 200

@app.route('/ship', methods=['POST'])
def ship():
    data = request.get_json() or {}
    order_id = data.get('order_id', 'unknown')

    log_structured("Iniciando envio do pedido", severity="INFO", order_id=order_id)

    db.collection("order_summaries").document(str(order_id)).update({
        "status": "SHIPPING_INITIATED",
        "updated_at": firestore.SERVER_TIMESTAMP
    })

    # Métrica: Pedido Pronto para Envio (Sucesso final do pipeline)
    report_experience_metric("order_shipped")

    log_structured("Envio iniciado com sucesso", severity="INFO", order_id=order_id, extra={"step": "03"})
    return jsonify({"status": "shipped"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
