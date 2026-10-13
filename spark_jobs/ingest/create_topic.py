from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

def create_kafka_topic():
    admin_client = KafkaAdminClient(
        bootstrap_servers="localhost:9092", 
        client_id='admin_script'
    )

    topic_list = [
        NewTopic(name="transactions", num_partitions=3, replication_factor=1)
    ]
    
    try:
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print("Tạo topic 'transactions' thành công!")
    except TopicAlreadyExistsError:
        print("Topic 'transactions' đã tồn tại sẵn từ trước.")
    except Exception as e:
        print(f"Lỗi khi tạo topic: {e}")
    finally:
        admin_client.close()

if __name__ == "__main__":
    create_kafka_topic()