from kafka.admin import KafkaAdminClient, NewTopic
import os

KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

def create_kafka_topic(topic_name: str, num_partitions=1, replication_factor=1):
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_SERVERS.split(','))
        existing = admin_client.list_topics()
        if topic_name not in existing:
            topic = NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)
            admin_client.create_topics([topic])
            print(f"[Kafka] Created topic: {topic_name}")
        else:
            print(f"[Kafka] Topic already exists: {topic_name}")
    except Exception as e:
        print(f"[Kafka] Failed to create topic: {e}")