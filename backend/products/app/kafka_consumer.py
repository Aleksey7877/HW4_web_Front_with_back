from kafka import KafkaConsumer
import threading
import os
import json

KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

def start_consumer():
    def consume():
        print("👂 Kafka consumer started")
        consumer = KafkaConsumer(
            "products",
            bootstrap_servers=KAFKA_SERVERS.split(','),
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id="products-service-consumer",
            auto_offset_reset="earliest",
            enable_auto_commit=True
        )
        for msg in consumer:
            print(f"Consumed message: {msg.value}")

    thread = threading.Thread(target=consume, daemon=True)
    thread.start()