#!/usr/bin/python
import psycopg2
from src.configuration import databaseconfig

def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE metrics(
                metric_name VARCHAR (50) PRIMARY KEY, 
                metric_desc VARCHAR (255) NOT NULL
                )
        """,
        """ CREATE TABLE channels(
                channel_name VARCHAR (50) PRIMARY KEY,
                channel_meta text UNIQUE
                )
        """,
        """
        create table stats
                (
                 metric_name varchar(50) not null
                  constraint stats_metrics_metric_name_fk
                   references metrics,
                 metric_value integer not null,
                 channel_name varchar(50) not null,
                 start_time TIMESTAMP not null,
                 end_time TIMESTAMP not null,
                 epoch_id bigint,
                 global_id BIGSERIAL,
                 constraint stats_pk
                  primary key (epoch_id, global_id)
                );
                create index stats_channel_name_index
                 on stats (channel_name);
                create index stats_end_time_index
                 on stats (end_time);
        """
    )
    conn = None
    try:
        # read connection parameters
        params = databaseconfig.dbconfig()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()