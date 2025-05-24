import json
import os
from kafka import KafkaProducer

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
        value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
    )
except Exception as e:
    print(f"[Kafka] Failed to init producer: {e}")
    producer = None

def send_kafka_event(topic: str, event: dict):
    if not producer:
        print("[Kafka] Producer is not available.")
        return
    try:
        producer.send(topic, event)
        producer.flush()
        print(f"[Kafka] Event sent to '{topic}': {event}")
    except Exception as e:
        print(f"[Kafka] Failed to send event: {e}")
