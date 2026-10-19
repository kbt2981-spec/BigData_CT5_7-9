import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

def create_kafka_topic():
    print("--> Dang khoi tao Kafka Topic: transactions...")
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers="localhost:9092", 
            client_id='admin_script'
        )

        topic_list = [
            NewTopic(name="transactions", num_partitions=3, replication_factor=1)
        ]
        
        try:
            admin_client.create_topics(new_topics=topic_list, validate_only=False)
            print("--> Tao topic 'transactions' thanh cong!")
        except TopicAlreadyExistsError:
            print("--> Topic 'transactions' da ton tai tu truoc.")
        except Exception as e:
            print(f"--> Thong bao tao topic: {e}")
        finally:
            admin_client.close()
    except Exception as ex:
        print(f"[!] Loi ket noi Kafka AdminClient: {ex}")

if __name__ == "__main__":
    create_kafka_topic()