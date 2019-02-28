from six.moves import configparser
import psycopg2


class DatabaseOperations():

    def __init__(self):
        config = configparser.ConfigParser().read('config.ini')
        self.db_name = config.get('dbauth', 'dbname')
        self.db_user = config.get('dbauth', 'user')
        self.db_pass = config.get('dbauth', 'password')
        self.db_host = config.get('dbauth', 'host')
        self.db_port = config.get('dbauth', 'port')

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

    def run_query(self, query):
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

