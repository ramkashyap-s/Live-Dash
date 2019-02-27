# Live-Dash
Stream processing pipeline for analyzing live chat data

## Architecture
![Alt text](docs/pipeline.png "Architecture")

Live-Dash runs a pipeline on the AWS cloud, using the following cluster configurations:

- 1 t2.large EC2 RDS PostgreSQL instance
- 3 m4.large EC2 instances for Kafka brokers and Kafka producers
- 3 m4.large EC2 instances for Spark 
- 1 t2.medium Web-Server

## Setup
- I used pegasus to spin up my clusters. You might want to use [the following](src/README.md)
to setup the enviornment on your localhost to test this out. 

