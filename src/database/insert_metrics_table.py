#!/usr/bin/python
import psycopg2
from src.database import database_config


def insert_metric(metric_name, metric_desc):
    """ insert a new metric into the metrics table """
    sql = """INSERT INTO metrics(metric_name, metric_desc)
             VALUES(%s, %s);"""
    conn = None
    try:
        # read database configuration
        params = database_config.dbconfig()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (metric_name, metric_desc))
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


# if __name__ == '__main__':
#     insert_metric('postgresql')
