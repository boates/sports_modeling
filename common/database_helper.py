"""
database_helper.py
Author: Brian Boates
"""
import sys
sys.dont_write_bytecode = True
import MySQLdb as mdb

class DatabaseHelper(object):
    """
    """
    def __init__(self, database_name='nhl', host='localhost', user='root'):
        self._database_name = database_name
        try:
            self.connection = mdb.connect(host=host, user=user, db=self.get_database_name())
            self.connection.autocommit(True)
            self.cursor = self.connection.cursor()
        except:
            print 'Problem establishing MySQL connection - exiting...'
            sys.exit(1)

    def __str__(self):
        s  = '<DatabaseHelper: '
        s += 'database_name=%s>' % self.get_database_name()
        return s

    def __repr__(self):
        return self.__str__()

    def get_database_name(self):
        return self._database_name

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def drop_database(self):
        self.cursor.execute("DROP DATABASE IF EXISTS "+self.get_database_name())

    def create_database(self):
        self.cursor.execute("CREATE SCHEMA IF NOT EXISTS "+self.get_database_name())
        self.cursor.execute("USE "+self.get_database_name())

    def execute_query(self, query):
        self.cursor.execute(query)

    def execute_queries(self, queries):
        for query in queries:
            self.execute_query(query)

    def get_query_results(self, query):
        self.execute_query(query)
        return self.cursor.fetchall()


def main():
    database_helper = DatabaseHelper()


if __name__ == '__main__':
    main()
