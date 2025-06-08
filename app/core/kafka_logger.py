import json
import logging
from datetime import datetime
from typing import Dict, Any
from kafka import KafkaProducer
from app.core.config import settings

class KafkaLogHandler(logging.Handler):
    """Custom logging handler que envia logs para Kafka"""
    
    def __init__(self):
        super().__init__()
        self.producer = None
        self.topic = "callerwatch-logs"
        self._init_producer()
    
    def _init_producer(self):
        """Inicializar produtor Kafka"""
        try:
            # 🔥 CORREÇÃO: usar configuração correta
            bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
            if isinstance(bootstrap_servers, str):
                bootstrap_servers = [bootstrap_servers]
            
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                # 🆕 Configurações adicionais para melhor conectividade
                retries=3,
                retry_backoff_ms=1000,
                request_timeout_ms=30000,
                api_version=(0, 10, 1)
            )
            print(f"✅ Kafka producer conectado: {bootstrap_servers}")
        except Exception as e:
            print(f"❌ Erro ao conectar Kafka: {e}")
            self.producer = None
    
    def emit(self, record):
        """Enviar log para Kafka"""
        if not self.producer:
            return
        
        try:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "service": "callerwatch-api"
            }
            
            # Adicionar informações extras se existirem
            if hasattr(record, 'user_id'):
                log_data['user_id'] = record.user_id
            if hasattr(record, 'ip'):
                log_data['ip'] = record.ip
            if hasattr(record, 'endpoint'):
                log_data['endpoint'] = record.endpoint
            
            # Enviar para Kafka
            future = self.producer.send(
                self.topic,
                key=record.levelname,
                value=log_data
            )
            
            # 🆕 Confirmar envio
            future.add_callback(lambda metadata: print(f"✅ Log enviado para Kafka: {metadata.topic}:{metadata.partition}"))
            future.add_errback(lambda exception: print(f"❌ Erro ao enviar log: {exception}"))
            
        except Exception as e:
            print(f"Erro ao enviar log para Kafka: {e}")

def setup_kafka_logging():
    """Configurar logging com Kafka"""
    kafka_handler = KafkaLogHandler()
    kafka_handler.setLevel(logging.INFO)
    
    # Aplicar o handler aos loggers principais
    loggers = [
        logging.getLogger("app"),
        logging.getLogger("app.routers"),
        logging.getLogger("app.services"),
    ]
    
    for logger in loggers:
        logger.addHandler(kafka_handler)
    
    return kafka_handler