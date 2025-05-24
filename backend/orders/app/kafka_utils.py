import os
from kafka.admin import KafkaAdminClient, NewTopic

KAFKA_TOPIC = "orders"
KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092").split(",")

def create_kafka_topic():
    try:
        admin = KafkaAdminClient(bootstrap_servers=KAFKA_SERVERS)
        topics = admin.list_topics()
        if KAFKA_TOPIC not in topics:
            admin.create_topics([NewTopic(name=KAFKA_TOPIC, num_partitions=1, replication_factor=1)])
            print(f"[Kafka] Created topic: {KAFKA_TOPIC}")
        else:
            print(f"[Kafka] Topic already exists: {KAFKA_TOPIC}")
    except Exception as e:
        print(f"[Kafka] Topic init failed: {e}")
