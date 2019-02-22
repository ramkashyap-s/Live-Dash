from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import sys
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.types import NumericType
import pyspark.sql.functions as func
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json
from pyspark.sql.functions import *
from pyspark.sql import DataFrame
from pyspark.sql import streaming
from six.moves import configparser

def postgres_sink(df, epoch_id):
    db_config = configparser.ConfigParser()
    if df.count() > 0:
        print("rows present")
        # df.show()
        db_config.read('config.ini')
        dbname = db_config.get('dbauth', 'dbname')
        dbuser = db_config.get('dbauth', 'user')
        dbpass = db_config.get('dbauth', 'password')
        dbhost = db_config.get('dbauth', 'host')
        dbport = db_config.get('dbauth', 'port')

        url = "jdbc:postgresql://"+dbhost+":"+dbport+"/"+dbname
        properties = {
            "driver": "org.postgresql.Driver",
            "user": dbuser,
            "password": dbpass
        }
        # print(properties)
        mode = 'append'
        df.write.jdbc(url=url, table="stats", mode=mode,
                              properties=properties)



if __name__ == "__main__":


    # if len(sys.argv) != 4:
    #     print("Usage: spark-submit name.py <hostname> <port> <topic>",
    #             file=sys.stderr)
    #     exit(-1)
    #
    # host = sys.argv[1]
    # port = sys.argv[2]
    # topic = sys.argv[3]
    spark_config = configparser.ConfigParser()
    spark_config.read('src/spark_streaming/config.ini')
    kafka_brokers = spark_config.get('spark', 'kafka_brokers')
    kafka_topic = spark_config.get('spark', 'kafka_topic')

    struct_schema = StructType([
        StructField("channel_name", StringType()),
        StructField("username", StringType()),
        StructField("message", StringType()),
        StructField("timestamp", StringType()),
        StructField("views", StringType()),
    ])
    # schema = StructType([StructField("channel_name", StringType())])

    spark = SparkSession\
        .builder\
        .appName("TwitchCommentsAnalysis")\
        .getOrCreate()
    print(kafka_brokers)
    print(kafka_topic)    
    spark.sparkContext.setLogLevel("ERROR")
    messageDFRaw = spark.readStream\
                        .format("kafka")\
                        .option("kafka.bootstrap.servers", kafka_brokers)\
                        .option("subscribe", kafka_topic) \
                        .option("startingOffsets", "latest") \
                        .load()

    messageDF = messageDFRaw.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

    messageCastedDF = messageDF.select(from_json("value", struct_schema).alias("message"))

    message_flattened_DF = messageCastedDF.selectExpr("message.channel_name", "message.username", "message.message",
                                                    "message.timestamp", "CAST(message.views AS LONG)")

    message_flattened_DF = message_flattened_DF.withColumn("timestamp", to_timestamp("timestamp"))

    print(messageDFRaw.printSchema())

    # print(messageDF.printSchema())
    #
    # print(messageCastedDF.printSchema())

    print(message_flattened_DF.printSchema())




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

    windowed_positive_count = message_flattened_DF \
                                     .withWatermark("timestamp", "10 seconds") \
                                     .where(message_flattened_DF["sentiment"] == "POSITIVE")\
                                     .groupBy(
                                            window("timestamp",
                                                    "5 seconds",
                                                    "1 seconds"),
                                            "channel_name")\
                                     .count()
                                     # .orderBy("count", ascending=False)

    # rename columns to match database schema
    windowed_positive_count = windowed_positive_count.selectExpr('window.end', 'channel_name', 'count')
    column_schema = ['time_window', 'channel_name', 'num_positive_comments']
    windowed_positive_count = windowed_positive_count.toDF('time_window', 'channel_name', 'metric_value')
    windowed_positive_count = windowed_positive_count.withColumn('metric_name', lit('num_positive_comments'))
    windowed_positive_count.printSchema()


    # count by sentiment
    messageDFSentimentCount = message_flattened_DF.select("sentiment") \
        .groupby("sentiment") \
        .count()




    windowed_message_count = message_flattened_DF \
                                     .withWatermark("timestamp", "5 seconds")\
                                     .groupBy(
                                            window("timestamp",
                                                    "5 seconds",
                                                    "1 seconds"),
                                            "channel_name")\
                                     .count()
                                     # .orderBy("count", ascending=False)


    # rename columns to match database schema
    windowed_message_count = windowed_message_count.selectExpr('window.end', 'channel_name', 'count')
    windowed_message_count = windowed_message_count.toDF('time_window', 'channel_name', 'metric_value')
    windowed_message_count = windowed_message_count.withColumn('metric_name', lit('num_comments'))
    # windowed_message_count.printSchema()




    windowed_view_counts = message_flattened_DF \
                                     .withWatermark("timestamp", "5 seconds")\
                                     .groupBy(
                                            window("timestamp",
                                                    "5 seconds",
                                                    "1 seconds"),
                                            "channel_name")\
                                     .avg("views")

    windowed_view_counts = windowed_view_counts.withColumn("avg(views)", func.round(windowed_view_counts["avg(views)"]))\
                                                .withColumnRenamed("avg(views)", "views")

    # windowed_view_counts.printSchema()

    # windowed_view_counts.printSchema()
    windowed_view_counts = windowed_view_counts.selectExpr('window.end', 'channel_name', 'views')
    # rename columns to match database schema
    windowed_view_counts = windowed_view_counts.toDF('time_window', 'channel_name', 'metric_value')
    windowed_view_counts = windowed_view_counts.withColumn('metric_name', lit('num_views'))
    # windowed_view_counts.printSchema()

    # windowed_view_counts = windowed_view_counts.withColumn('time_window', )

    message_count_query = windowed_message_count.writeStream \
        .outputMode("append") \
        .foreachBatch(postgres_sink) \
        .option("truncate", "false") \
        .trigger(processingTime="1 seconds") \
        .start()

    positive_message_count_query = windowed_positive_count.writeStream \
        .outputMode("append") \
        .foreachBatch(postgres_sink) \
        .option("truncate", "false") \
        .trigger(processingTime="1 seconds") \
        .start()

    # view_counts_query = windowed_view_counts.writeStream \
    #     .outputMode("append") \
    #     .foreachBatch(postgres_sink) \
    #     .option("truncate", "false") \
    #     .trigger(processingTime="1 seconds") \
    #     .start()

    spark.streams.awaitAnyTermination()

    # view_counts_query = windowed_view_counts.writeStream \
    #     .outputMode("append") \
    #     .format("console") \
    #     .option("truncate", "false") \
    #     .trigger(processingTime="5 seconds") \
    #     .start() \
    #     .awaitTermination()


    # query = messageDFSentimentCount.writeStream\
    #                                 .outputMode("complete")\
    #                                 .format("console")\
    #                                 .option("truncate", "false")\
    #                                 .trigger(processingTime="5 seconds")\
    #                                 .start()\
    #                                 .awaitTermination()


