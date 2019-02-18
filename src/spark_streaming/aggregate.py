import os
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.types import NumericType
import pyspark.sql.functions as func

import time
# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
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

    struct_schema = StructType([
        StructField("channel", StringType()),
        StructField("username", StringType()),
        StructField("message", StringType()),
        StructField("timestamp", StringType()),
        StructField("views", StringType()),
    ])
    # schema = StructType([StructField("channel", StringType())])

    spark = SparkSession\
        .builder\
        .appName("TwitchCommentsAnalysis")\
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")
    messageDFRaw = spark.readStream\
                        .format("kafka")\
                        .option("kafka.bootstrap.servers", 'localhost:9092')\
                        .option("subscribe", "twitch-parsed-message") \
                        .option("startingOffsets", "latest") \
                        .load()

    messageDF = messageDFRaw.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

    messageCastedDF = messageDF.select(from_json("value", struct_schema).alias("message"))

    message_flattened_DF = messageCastedDF.selectExpr("message.channel", "message.username", "message.message",
                                                    "message.timestamp", "CAST(message.views AS LONG)")

    message_flattened_DF = message_flattened_DF.withColumn("timestamp", to_timestamp("timestamp"))


    # messageFlattenedDF = messageFlattenedDF.withWatermark("impressionTime", "60 seconds")

    # messageDFRaw.selectExpr(from_json("CAST(value AS STRING)", struct_schema))

    # messageDF = messageDFRaw.toJSON()
    # messageDF = messageDFRaw.selectExpr("CAST(value AS STRING) as message")

    # messageDF = messageDFRaw.select(from_json(col("value").cast("string").schema))



    # messageDF = messageDF.selectExpr("message AS json")
    # print(messageDF.isStreaming)
    # print(messageDF.printSchema())
    # query = messageDF.writeStream.format("console").start()
    # time.sleep(10)  # sleep 10 seconds
    # query.stop()
    print(messageDFRaw.printSchema())

    print(messageDF.printSchema())

    print(messageCastedDF.printSchema())

    print(message_flattened_DF.printSchema())

    # messageDF = messageDFRaw.select("CAST(value AS STRING)")

    # messageDF = messageDFRaw.select(from_json(col("value").cast("string"), struct))
    # messageNestedDf = messageDF.select(from_json("value", struct).as("message"))


    # afinn = Afinn()

    # function for sentiment score
    def add_sentiment_score(text):
        analyzer = SentimentIntensityAnalyzer()
        sentiment_score = analyzer.polarity_scores(text)
        # sentiment_score = afinn.score(text)
        return sentiment_score['compound']


    add_sentiment_score_udf = udf(
        add_sentiment_score,
        FloatType()
    )

    message_flattened_DF = message_flattened_DF.withColumn(
        "sentiment_score",
        add_sentiment_score_udf(message_flattened_DF.message)
    )

    # function for sentiment grade
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
    message_flattened_DF = message_flattened_DF.withColumn(
        "sentiment",
        add_sentiment_grade_udf("sentiment_score")
    )
    # messageFlattenedDF.withWatermark("timestamp", "15 seconds")

    windowed_user_counts = message_flattened_DF \
                                     .withWatermark("timestamp", "15 seconds")\
                                     .groupBy(
                                            window("timestamp",
                                                    "15 seconds",
                                                    "5 seconds"),
                                            "channel")\
                                     .count()\
                                     .orderBy("count", ascending=False)

    windowed_view_counts = message_flattened_DF \
                                     .withWatermark("timestamp", "15 seconds")\
                                     .groupBy(
                                            window("timestamp",
                                                    "5 seconds",
                                                    "1 seconds"),
                                            "channel")\
                                     .avg("views")

    windowed_view_counts = windowed_view_counts.withColumn("avg(views)", func.round(windowed_view_counts["avg(views)"]))\
                                           .withColumnRenamed("avg(views)", "views")

    windowed_sentiment = message_flattened_DF \
                                     .withWatermark("timestamp", "60 seconds") \
                                     .where(message_flattened_DF["sentiment"] == "POSITIVE")\
                                     .groupBy(
                                            window("timestamp",
                                                    "15 seconds",
                                                    "5 seconds"),
                                            "channel")\
                                     .count()
                                     # .orderBy("count", ascending=False)


    # count by sentiment
    messageDFSentimentCount = message_flattened_DF.select("sentiment") \
        .groupby("sentiment") \
        .count()

    view_counts_query = windowed_view_counts.writeStream \
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



