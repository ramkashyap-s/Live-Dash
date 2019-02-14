import psycopg2
from src.configuration import databaseconfig


def insert_stats_list(stats_list):
    """ insert multiple vendors into the vendors table  """
    sql = "INSERT INTO stats(channel_name, time_window, metric_name, metric_value) " \
          "VALUES(%int, %timestamp, %int, %int)"
    conn = None
    try:
        # read database configuration
        params = databaseconfig.dbconfig()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.executemany(sql,stats_list)
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()