#!/usr/bin/env bash

#to start sending messages to broker
python3 run_bot.py

# for submitting spark application to master
spark-submit \
--packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0,org.postgresql:postgresql:42.2.5  \
--master spark://<hostname>:7077
/src/spark_streaming/aggregate.py

# to run spark application locally
spark-submit \
--packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0,org.postgresql:postgresql:42.2.5  \
/src/spark_streaming/aggregate.py

