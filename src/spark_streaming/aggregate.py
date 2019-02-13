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
from afinn import Afinn
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
    # sqlContext.read.json(rdd)
    # messageDF = messageDFRaw.selectExpr("value")
    # messageDF = messageDFRaw.select(from_json(col("value").cast("string").schema))
    # messageDF = messageDFRaw.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

    messageDF = messageDFRaw.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING) as message")
    # messageDF = messageDF.selectExpr("message AS json")
    # print(messageDF.isStreaming)
    # print(messageDF.printSchema())
    # query = messageDF.writeStream.format("console").start()
    #
    # time.sleep(10)  # sleep 10 seconds
    # query.stop()

    afinn = Afinn()


    def add_sentiment_score(text):

        sentiment_score = afinn.score(text)
        return sentiment_score


    add_sentiment_score_udf = udf(
        add_sentiment_score,
        FloatType()
    )

    messageDF = messageDF.withColumn(
        "score",
        add_sentiment_score_udf(messageDF.message)
    )


    def add_sentiment_grade(score):

        if score < 0:
            return 'NEGATIVE'
        elif score == 0:
            return 'NEUTRAL'
        else:
            return 'POSITIVE'


    add_sentiment_grade_udf = udf(
        add_sentiment_grade,
        StringType()
    )
    messageDF = messageDF.withColumn(
        "grade",
        add_sentiment_grade_udf("score")
    )

    messageDFSentimentCount = messageDF.select("grade") \
        .groupby("grade") \
        .count()

    query = messageDF.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .trigger(processingTime="5 seconds") \
        .start() \
        .awaitTermination()

    # query = messageDFSentimentCount.writeStream\
    #                                 .outputMode("complete")\
    #                                 .format("console")\
    #                                 .option("truncate", "false")\
    #                                 .trigger(processingTime="5 seconds")\
    #                                 .start()\
    #                                 .awaitTermination()




