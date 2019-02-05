import os
from pyspark.sql import SparkSession
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql.functions import *

from pyspark.sql import DataFrame
from pyspark.sql import streaming


# class Aggregations:
#         def engagement_aggregator(spark):
