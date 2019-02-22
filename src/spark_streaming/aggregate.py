from pyspark.sql import SparkSession
from pyspark.sql.types import *
import pyspark.sql.functions as func
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from pyspark.sql.functions import *

from six.moves import configparser

def postgres_sink(df, epoch_id):
    config = configparser.ConfigParser()
    if df.count() > 0:
        # print("rows present")
        df.show()
        config.read('src/spark_streaming/config.ini')
        dbname = config.get('dbauth', 'dbname')
        dbuser = config.get('dbauth', 'user')
        dbpass = config.get('dbauth', 'password')
        dbhost = config.get('dbauth', 'host')
        dbport = config.get('dbauth', 'port')

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




if __name__ == "__main__":


    # if len(sys.argv) != 4:
    #     print("Usage: spark-submit spark_aggregation.py <hostname> <port> <topic>",
    #             file=sys.stderr)
    #     exit(-1)
    #
    # host = sys.argv[1]
    # port = sys.argv[2]
    # topic = sys.argv[3]

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

    spark.sparkContext.setLogLevel("ERROR")
    messageDFRaw = spark.readStream\
                        .format("kafka")\
                        .option("kafka.bootstrap.servers", 'localhost:9092')\
                        .option("subscribe", "twitch-parsed-message") \
                        .option("startingOffsets", "latest") \
                        .load()

    messageDF = messageDFRaw.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

    messageCastedDF = messageDF.select(from_json("value", struct_schema).alias("message"))

    message_flattened_DF = messageCastedDF.selectExpr("message.channel_name", "message.username", "message.message",
                                                    "message.timestamp", "CAST(message.views AS LONG)")

    message_flattened_DF = message_flattened_DF.withColumn("timestamp", to_timestamp("timestamp"))

    # print(messageDFRaw.printSchema())
    # print(messageDF.printSchema())
    # print(messageCastedDF.printSchema())
    # print(message_flattened_DF.printSchema())

    add_sentiment_score_udf = udf(
        add_sentiment_score,
        FloatType()
    )

    message_flattened_DF = message_flattened_DF.withColumn(
        "sentiment_score",
        add_sentiment_score_udf(message_flattened_DF.message)
    )


    add_sentiment_grade_udf = udf(
        add_sentiment_type,
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
                                            window("timestamp", "5 seconds", "1 seconds"),
                                            "channel_name")\
                                     .count()

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
                                            window("timestamp", "5 seconds", "1 seconds"),
                                            "channel_name")\
                                     .count()

    # rename columns to match database schema
    windowed_message_count = windowed_message_count.selectExpr('window.end', 'channel_name', 'count')
    windowed_message_count = windowed_message_count.toDF('time_window', 'channel_name', 'metric_value')
    windowed_message_count = windowed_message_count.withColumn('metric_name', lit('num_comments'))
    windowed_message_count.printSchema()

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

    # select and rename columns to match database schema
    windowed_view_counts = windowed_view_counts.selectExpr('window.end', 'channel_name', 'views')
    windowed_view_counts = windowed_view_counts.toDF('time_window', 'channel_name', 'metric_value')
    windowed_view_counts = windowed_view_counts.withColumn('metric_name', lit('num_views'))
    windowed_view_counts.printSchema()

    # query for counting number of messages
    message_count_query = windowed_message_count.writeStream \
        .outputMode("append") \
        .foreachBatch(postgres_sink) \
        .option("truncate", "false") \
        .trigger(processingTime="1 seconds") \
        .start()

    # query for counting number of positive messages
    positive_message_count_query = windowed_positive_count.writeStream \
        .outputMode("append") \
        .foreachBatch(postgres_sink) \
        .option("truncate", "false") \
        .trigger(processingTime="1 seconds") \
        .start()

    spark.streams.awaitAnyTermination()

