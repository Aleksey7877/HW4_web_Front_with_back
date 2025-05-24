import os
import json
import threading
from kafka import KafkaConsumer

KAFKA_TOPIC = "orders"
KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092").split(",")

def handle_event(event: dict):
    action = event.get("action")
    print(f"Kafka received event: {action.upper()} — {event}")

def start_kafka_consumer():
    def consume():
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_SERVERS,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                group_id="orders-consumer-group"
            )
            print(f"Kafka consumer started on topic '{KAFKA_TOPIC}'")
            for message in consumer:
                handle_event(message.value)
        except Exception as e:
            print(f"Kafka consumer error: {e}")

    thread = threading.Thread(target=consume, daemon=True)
    thread.start()
