import os
# os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.11:2.4.0 pyspark-shell'
from pyspark.sql import SparkSession
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql.functions import *
# from pyspark import
from pyspark.sql import DataFrame
from pyspark.sql import streaming
#    Spark
from pyspark import SparkContext
#    Spark Streaming
from pyspark.streaming import StreamingContext
#    Kafka
from pyspark.streaming.kafka import KafkaUtils
#    json parsing
import json

# class Aggregations:
#         def stats_calculator(self):
#             # Construct a streaming DataFrame that reads from topic1
#             df = spark_session \
#               .readStream \
#               .format("kafka") \
#               .option("kafka.bootstrap.servers", "localhost:9092") \
#               .option("subscribe", "twitch-message") \
#               .option("startingOffsets", "earliest") \
#               .load()
#             df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
#             df.count()
#             df.show()

if __name__ == "__main__":
    ss = SparkSession.builder.appName("twitch-stats").getOrCreate()
    sc = ss.sparkContext
    # sc = SparkContext(appName="twitch-stats")
    #.config("spark.executor.cores", "4").config("spark.executor.memory", "4g")
    sc.setLogLevel("WARN")
    ssc = StreamingContext(sc, 60)

    # kafkaStream = KafkaUtils.createStream(ssc,'localhost:2181', 'spark-streaming', {'twitch-message':1})

    # twitchAggregator = Aggregations()
    # twitchAggregator.stats_calculator()

    # df = spark_session \
    #     .readStream \
    #     .format("kafka") \
    #     .option("kafka.bootstrap.servers", "localhost:2181") \
    #     .option("subscribe", "twitch-message") \
    #     .option("startingOffsets", "earliest") \
    #     .load()
    # df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
    # print(df.isStreaming)
    # df.printSchema()
    #

