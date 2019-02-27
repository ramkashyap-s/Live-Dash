#!/usr/bin/env bash

CLUSTER_NAME=spark-cluster

peg up $PRJ_DIR/setup/spark/master.yml &
peg up $PRJ_DIR/setup/spark/workers.yml &
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
peg install ${CLUSTER_NAME} spark
wait

peg service ${CLUSTER_NAME} hadoop start
peg service ${CLUSTER_NAME} spark start