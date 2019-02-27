from pyspark.sql import SparkSession
from pyspark.sql.types import *
import pyspark.sql.functions as func
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pyspark.sql.functions import *
from six.moves import configparser
import os

# ToDO: move the functions into a class and refactor this file

def postgres_sink(df, epoch_id):
    db_config = configparser.ConfigParser()
    if df.count() > 0:
        print("rows are present")
        # df.show()
        path = '/home/' + os.getlogin() + '/Live-Dash/config.ini'
        db_config.read(path)
        dbname = db_config.get('dbauth', 'dbname')
        dbuser = db_config.get('dbauth', 'user')
        dbpass = db_config.get('dbauth', 'password')
        dbhost = db_config.get('dbauth', 'host')
        dbport = db_config.get('dbauth', 'port')

        df = df.withColumn('epoch_id', lit(epoch_id))
        url = "jdbc:postgresql://"+dbhost+":"+dbport+"/"+dbname
        properties = {
            "driver": "org.postgresql.Driver",
            "user": dbuser,
            "password": dbpass
        }
        mode = 'append'
        df.write.jdbc(url=url, table="stats", mode=mode,
                              properties=properties)
    else:
        print("rows are not present")


# function for sentiment score
def add_sentiment_score(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)
    return sentiment_score['compound']


# function for sentiment type
def add_sentiment_type(score):

    if score < 0:
        return 'NEGATIVE'
    elif score == 0:
        return 'NEUTRAL'
    else:
        return 'POSITIVE'

# function for calculating number of comments grouped by channel
def num_comments(df, time_window, sliding_interval, watermark):
    windowed_message_count = df \
                                 .withWatermark("timestamp", watermark)\
                                 .groupBy(
                                        window("timestamp", time_window, sliding_interval),
                                        "channel_name")\
                                 .count()

    # rename columns to match database schema
    windowed_message_count = windowed_message_count.selectExpr('window.end', 'channel_name', 'count')
    windowed_message_count = windowed_message_count.toDF('time_window', 'channel_name', 'metric_value')
    windowed_message_count = windowed_message_count.withColumn('metric_name', lit('num_comments'))

    # query for counting number of messages and writing it into postgres
    message_count_query = windowed_message_count.writeStream \
        .outputMode("append") \
        .foreachBatch(postgres_sink) \
        .option("truncate", "false") \
        .start()

# function for calculating number of comments grouped by channel
def num_views(df, time_window, sliding_interval, watermark):
    windowed_view_counts = df \
                             .withWatermark("timestamp", watermark)\
                             .groupBy(
                                    window("timestamp", time_window,sliding_interval),
                                    "channel_name")\
                             .avg("views")

    windowed_view_counts = windowed_view_counts.withColumn("avg(views)", func.round(windowed_view_counts["avg(views)"]))\
                                                .withColumnRenamed("avg(views)", "views")


    # select and rename columns to match database schema
    windowed_view_counts = windowed_view_counts.selectExpr('window.end', 'channel_name', 'views')
    windowed_view_counts = windowed_view_counts.toDF('time_window', 'channel_name', 'metric_value')
    windowed_view_counts = windowed_view_counts.withColumn('metric_name', lit('num_views'))


    # query for counting number of positive messages
    view_count_query = windowed_view_counts.writeStream \
        .outputMode("append") \
        .foreachBatch(postgres_sink) \
        .option("truncate", "false") \
        .start()


# function for calculating number of positive comments grouped by channel
def num_positive_comments(df, time_window, sliding_interval, watermark):
    add_sentiment_score_udf = udf(
        add_sentiment_score,
        FloatType()
    )

    df = df.withColumn(
        "sentiment_score",
        add_sentiment_score_udf(df.message)
    )

    add_sentiment_grade_udf = udf(
        add_sentiment_type,
        StringType()
    )
    df = df.withColumn(
        "sentiment",
        add_sentiment_grade_udf("sentiment_score")
    )

    windowed_positive_count = df \
                                 .withWatermark("timestamp", watermark) \
                                 .where(df["sentiment"] == "POSITIVE")\
                                 .groupBy(
                                        window("timestamp", time_window, sliding_interval),
                                        "channel_name")\
                                 .count()

    # rename columns to match database schema
    windowed_positive_count = windowed_positive_count.selectExpr('window.end', 'channel_name', 'count')
    windowed_positive_count = windowed_positive_count.toDF('time_window', 'channel_name', 'metric_value')
    windowed_positive_count = windowed_positive_count.withColumn('metric_name', lit('num_positive_comments'))

    # query for counting number of messages and writing it into postgres
    message_count_query = windowed_positive_count.writeStream \
        .outputMode("append") \
        .foreachBatch(postgres_sink) \
        .option("truncate", "false") \
        .start()


if __name__ == "__main__":

    spark_config = configparser.ConfigParser()
    # path = '/home/' + os.getlogin() + '/Live-Dash/config.ini'
    path = 'config.ini'
    spark_config.read(path)
    print(path)
    kafka_brokers = spark_config.get('spark', 'kafka_brokers')
    kafka_topic = spark_config.get('spark', 'kafka_topic')

    # define the schema for kafka messages
    struct_schema = StructType([
        StructField("channel_name", StringType()),
        StructField("username", StringType()),
        StructField("message", StringType()),
        StructField("timestamp", StringType()),
        StructField("views", StringType()),
    ])

    # define starting point for spark session
    spark = SparkSession\
        .builder\
        .appName("TwitchCommentsAnalysis")\
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    # subscribe to topic and read from kafka brokers
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

    num_positive_comments(message_flattened_DF, "10 seconds", "5 seconds", "1 second")
    num_comments(message_flattened_DF, "10 seconds", "5 seconds", "1 second")
    num_views(message_flattened_DF, "10 seconds", "5 seconds", "1 second")

    spark.streams.awaitAnyTermination()
