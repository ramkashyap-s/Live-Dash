#!/usr/bin/python
import psycopg2
from src.config import databaseconfig


def insert_metric(metric_name):
    """ insert a new vendor into the vendors table """
    sql = """INSERT INTO metrics(metric_name)
             VALUES(%s) RETURNING metric_id;"""
    conn = None
    vendor_id = None
    try:
        # read database configuration
        params = databaseconfig.dbconfig()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (metric_name,))
        # get the generated id back
        vendor_id = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return vendor_id

# if __name__ == '__main__':
#     insert_metric('postgresql')