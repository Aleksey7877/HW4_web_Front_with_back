import os
import json
from kafka import KafkaProducer

KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVERS.split(','),
    value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
    request_timeout_ms=1000,
    delivery_timeout_ms=1500,
    acks=0,
    retries=0,
    linger_ms=5,
)

def send_kafka_event(topic: str, event: dict):
    try:
        producer.send(topic, event)
    except Exception as e:
        print(f"Kafka send exception: {e}")