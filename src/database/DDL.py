#!/usr/bin/python
import psycopg2
from src.config import databaseconfig

def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE metrics(
                metric_id serial PRIMARY KEY, 
                metric_name VARCHAR (50) UNIQUE NOT NULL, 
                metric_desc VARCHAR (255) NOT NULL
                )
        """,
        """ CREATE TABLE channels(
                channel_id serial PRIMARY KEY, 
                channel_name VARCHAR (50) UNIQUE NOT NULL
                )
        """,
        """
        CREATE TABLE stats (
                channel_id INTEGER NOT NULL,
                previous_time_window TIMESTAMP NOT NULL,
                metric_id INTEGER NOT NULL,
                metric_value INTEGER NOT NULL,  
                PRIMARY KEY (channel_id, previous_time_window)                           
        )
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