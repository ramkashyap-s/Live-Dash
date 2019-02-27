#!/usr/bin/env bash

# spin up spark cluster
source $PRJ_DIR_DLIVE/setup/spark/spin-spark.sh

wait
echo "completed $CLUSTER_NAME"

# spin up kafka cluster
source $PRJ_DIR_DLIVE/setup/elasticsearch/spin-kafka.sh

wait
echo "completed $CLUSTER_NAME"

# spin up web-server node
source $PRJ_DIR_DLIVE/setup/application/spin-application.sh

wait
echo "completed $CLUSTER_NAME"