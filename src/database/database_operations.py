from six.moves import configparser
import psycopg2
import os

class DatabaseOperations:

    def __init__(self):
        db_config = configparser.ConfigParser()
        # path = '/home/ram/PycharmProjects/dash-live/config.ini'
        path = '/home/' + os.getlogin() + '/Live-Dash/config.ini'
        db_config.read(path)
        self.db_name = db_config.get('dbauth', 'dbname')
        self.db_user = db_config.get('dbauth', 'user')
        self.db_pass = db_config.get('dbauth', 'password')
        self.db_host = db_config.get('dbauth', 'host')
        self.db_port = db_config.get('dbauth', 'port')

        self.conn_properties = {
            "user": self.db_user,
            "password": self.db_pass,
            "database": self.db_name,
            "host": self.db_host,
            "port": self.db_port
        }
        try:
            self.conn = psycopg2.connect(**self.conn_properties)
            self.cursor = self.conn.cursor()
        except Exception as error:
            print('Error: connection not established {}'.format(error))

    def get_cursor(self):
        return self.cursor

    def get_connection(self):
        return self.conn

    def read(self, query):
        try:
            result = self.cursor.execute(query)
        except Exception as error:
            print('error execting query "{}", error: {}'.format(query, error))
            return None
        else:
            return result

    def del_connection(self):
        self.cursor.close()
        self.conn.close()

