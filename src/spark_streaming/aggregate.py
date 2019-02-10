import os
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json

from pyspark.sql.functions import *
from pyspark.sql import DataFrame
from pyspark.sql import streaming


if __name__ == "__main__":
    # Create a local StreamingContext with two working thread and batch interval of 3 second
    sc = SparkContext("local[2]", "OdometryConsumer")
    ssc = StreamingContext(sc, 3)
    kafkaStream = KafkaUtils.createDirectStream(ssc, ['twitch-message'], {'metadata.broker.list': 'localhost:9092'})
    parsed = kafkaStream.map(lambda v: json.loads(v))

    def f(x):
        x.take(10)

    fore = parsed.foreachRDD(f)
    parsed.pprint()
    ssc.start()  # Start the computation
    ssc.awaitTermination()  # Wait for the computation to terminate


