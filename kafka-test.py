import json
from kafka.consumer import KafkaConsumer

consumer = KafkaConsumer('my_topic',
                         bootstrap_servers=['127.0.0.1:9092'],
                         value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                         enable_auto_commit=False,
                         auto_offset_reset='earliest',
                         max_poll_records=100)

for message in consumer:
    print(message.value)

consumer.close()
