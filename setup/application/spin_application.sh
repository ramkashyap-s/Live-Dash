#!/usr/bin/env bash

CLUSTER_NAME=application-cluster

peg up $PRJ_DIR/setup/application/master.yml &

wait

peg fetch ${CLUSTER_NAME}

wait

peg install ${CLUSTER_NAME} ssh

wait

peg install ${CLUSTER_NAME} aws

wait

peg install ${CLUSTER_NAME} environment

wait