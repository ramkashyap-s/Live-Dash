import psycopg2
from src.configuration import databaseconfig


def insert_stats_list(stats_list):
    """ insert multiple rows into the table  """
    sql = "INSERT INTO stats(channel_name, end_time, metric_name, metric_value) " \
          "VALUES(%string, %timestamp, %string, %int)"
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