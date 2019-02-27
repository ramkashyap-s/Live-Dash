#!/usr/bin/env bash

CLUSTER_NAME=elastic-cluster

peg up $PRJ_DIR/setup/elasticsearch/master.yml &
peg up $PRJ_DIR/setup/elasticsearch/workers.yml &
wait

peg fetch ${CLUSTER_NAME}
wait

peg install ${CLUSTER_NAME} ssh
wait

peg install ${CLUSTER_NAME} aws
wait

peg install ${CLUSTER_NAME} environment
wait

peg install ${CLUSTER_NAME} hadoop
peg install ${CLUSTER_NAME} zookeeper
peg install ${CLUSTER_NAME} kafka

wait

peg service ${CLUSTER_NAME} hadoop start

peg sshcmd-cluster kafka-cluster "/usr/local/kafka/bin/zookeeper-server-start.sh /usr/local/kafka/config/zookeeper.properties &"

peg sshcmd-cluster kafka-cluster "sudo JMX_PORT=8004 /usr/local/kafka/bin/kafka-server-start.sh /usr/local/kafka/config/server.properties &"

