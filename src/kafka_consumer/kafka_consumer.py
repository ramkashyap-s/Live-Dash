# Test Kafka consumer to count number of emojis
from kafka import KafkaConsumer
import json
from emoji_extractor.extract import Extractor

def split_count(text):
    extract = Extractor()
    emoji_count = extract.count_emoji(text, check_first=True)
    return emoji_count

if __name__ == "__main__":
    # To consume latest messages and auto-commit offsets
    consumer = KafkaConsumer('twitch-message',
                             bootstrap_servers=['localhost:9092'],
                             auto_offset_reset='earliest', enable_auto_commit=False,
                             value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    num_messages = dict()
    num_emojis = dict()
    for message in consumer:
        print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                             message.offset, message.key,
                                             message.value))
        counter = split_count(message.value['message'])
        print("value=%s emojis = %s" % (message.value, counter))



