#!/usr/bin/env bash

# spin up spark cluster
source $DLIVE_PRJ_DIR_/setup/spark/spin-spark.sh

wait
echo "completed $CLUSTER_NAME"

# spin up kafka cluster
source $DLIVE_PRJ_DIR_/setup/elasticsearch/spin-kafka.sh

wait
echo "completed $CLUSTER_NAME"

# spin up web-server node
source $DLIVE_PRJ_DIR_/setup/application/spin-application.sh

wait
echo "completed $CLUSTER_NAME"