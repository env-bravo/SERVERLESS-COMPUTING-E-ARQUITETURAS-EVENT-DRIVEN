import os
import json
import logging
import time
from flask import Flask, request, jsonify
from google.cloud import firestore
import google.cloud.logging

# Configuração do Logging Estruturado
log_client = google.cloud.logging.Client()
log_client.setup_logging()

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

    # Log enriquecido para Log-based Metric (Substitui o SDK de Monitoring)
    log_structured("Reserva concluída com sucesso", severity="INFO", order_id=order_id, 
                   extra={"step": "01", "metric_event": "stock_reserved", "status": "success"})
    
    return jsonify({"status": "reserved"}), 200

@app.route('/charge', methods=['POST'])
def charge():
    data = request.get_json() or {}
    order_id = data.get('order_id', 'unknown')

    log_structured("Iniciando processamento de pagamento", severity="INFO", order_id=order_id)

    if order_id == "ORD-FAIL-RETRY":
        log_structured("Simulando falha transiente (503)", severity="ERROR", order_id=order_id,
                       extra={"metric_event": "payment_status", "status": "failure"})
        return "Service Unavailable", 503

    db.collection("order_summaries").document(str(order_id)).update({
        "status": "PAYMENT_PROCESSED",
        "updated_at": firestore.SERVER_TIMESTAMP
    })

    log_structured("Pagamento processado com sucesso", severity="INFO", order_id=order_id, 
                   extra={"step": "02", "metric_event": "payment_status", "status": "success"})
    
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

    log_structured("Envio iniciado com sucesso", severity="INFO", order_id=order_id, 
                   extra={"step": "03", "metric_event": "order_shipped"})
    
    return jsonify({"status": "shipped"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
