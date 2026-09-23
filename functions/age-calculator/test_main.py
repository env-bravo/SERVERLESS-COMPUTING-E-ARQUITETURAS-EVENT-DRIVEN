import pytest
import base64
import json
from main import calculate_age_pubsub
from unittest.mock import MagicMock

def test_calculate_age_success(capsys):
    # Mock CloudEvent
    data = base64.b64encode(json.dumps({'birth_date': '1990-01-01'}).encode('utf-8')).decode('utf-8')
    cloud_event = MagicMock()
    cloud_event.data = {"message": {"data": data}}
    
    calculate_age_pubsub(cloud_event)
    
    captured = capsys.readouterr()
    assert "Calculation Successful for 1990-01-01" in captured.out
    # Calculo dinâmico para não falhar dependendo do ano atual (2026 no sistema)
    assert '"years": 36' in captured.out 

def test_calculate_age_invalid_format(capsys):
    data = base64.b64encode(json.dumps({'birth_date': '01-01-1990'}).encode('utf-8')).decode('utf-8')
    cloud_event = MagicMock()
    cloud_event.data = {"message": {"data": data}}
    
    calculate_age_pubsub(cloud_event)
    
    captured = capsys.readouterr()
    assert "Error: Invalid date format. Use YYYY-MM-DD." in captured.out

def test_calculate_age_missing_field(capsys):
    data = base64.b64encode(json.dumps({}).encode('utf-8')).decode('utf-8')
    cloud_event = MagicMock()
    cloud_event.data = {"message": {"data": data}}
    
    calculate_age_pubsub(cloud_event)
    
    captured = capsys.readouterr()
    assert "Error: Please provide 'birth_date' in YYYY-MM-DD format in the Pub/Sub message." in captured.out
