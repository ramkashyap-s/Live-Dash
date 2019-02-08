from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import operator


if __name__ == "__main__":
    conf = SparkConf().setMaster("local[2]").setAppName("Streamer")
    sc = SparkContext(conf=conf)

    # Creating a streaming context with batch interval of 10 sec
    ssc = StreamingContext(sc, 10)
    kstream = KafkaUtils.createDirectStream(
        ssc, topics=['twitch-message'], kafkaParams={"metadata.broker.list": 'localhost:9092'})
    messages = kstream.map(lambda x: x[1].encode("ascii", "ignore"))
