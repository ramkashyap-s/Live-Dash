import os
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import time

import json
# from afinn import Afinn
from pyspark.sql.functions import *
from pyspark.sql import DataFrame
from pyspark.sql import streaming

import sys

if __name__ == "__main__":

    # if len(sys.argv) != 4:
    #     print("Usage: spark-submit m03_demo04_tweetSentiment.py <hostname> <port> <topic>",
    #             file=sys.stderr)
    #     exit(-1)
    #
    # host = sys.argv[1]
    # port = sys.argv[2]
    # topic = sys.argv[3]

    spark = SparkSession\
        .builder\
        .appName("TwitterSentimentAnalysis")\
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    messageDFRaw = spark.readStream\
                        .format("kafka")\
                        .option("kafka.bootstrap.servers", "localhost:9092")\
                        .option("subscribe", "twitch-message")\
                        .load()

    messageDF = messageDFRaw.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

    # messageDF = messageDFRaw.selectExpr("CAST(value AS STRING) as message")
    print(messageDF.isStreaming)
    print(messageDF.printSchema())
    # query = messageDF.writeStream.format("console").start()
    #
    # time.sleep(10)  # sleep 10 seconds
    # query.stop()

    query = messageDF.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .trigger(processingTime="5 seconds") \
        .start() \
        .awaitTermination()





