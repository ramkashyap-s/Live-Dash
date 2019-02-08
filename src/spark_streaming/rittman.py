import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2 pyspark-shell'

#    Spark
from pyspark import SparkContext
#    Spark Streaming
from pyspark.streaming import StreamingContext
#    Kafka
from pyspark.streaming.kafka import KafkaUtils
#    json parsing
import json

sc = SparkContext(appName="twitch-stats")
sc.setLogLevel("WARN")

ssc = StreamingContext(sc, 60)

kafkaStream = KafkaUtils.createStream(ssc,'localhost:2181', 'spark-streaming', {'twitch-message':1})

parsed = kafkaStream.map(lambda v: json.loads(v[1]))

print(parsed.count().map(lambda x:'messages in this batch: %s' % x).pprint())

# authors_dstream = parsed.map(lambda tweet: tweet['user']['screen_name'])
