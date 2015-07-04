"""
database_helper.py
Author: Brian Boates
"""
import MySQLdb as mdb

class DatabaseHelper(object):
    """
    """
    def __init__(self,
                 db=None,
                 host='localhost',
                 user='root'):
        self._db = db
        try:
            self.connection = mdb.connect(host=host, user=user, db=self.get_db())
            self.connection.autocommit(True)
            self.cursor = self.connection.cursor()
        except:
            print 'Problem establishing MySQL connection - exiting...'
            sys.exit(1)

    def __str__(self):
        s  = '<DatabaseHelper: '
        s += 'db=%s>' % self.get_db()
        return s

    def __repr__(self):
        return self.__str__()

    def get_db(self):
        return self._db

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def drop_database(self):
        self.cursor.execute("DROP DATABASE IF EXISTS "+self.get_db())

    def create_database(self):
        self.cursor.execute("CREATE SCHEMA IF NOT EXISTS "+self.get_db())
        self.cursor.execute("USE "+self.get_db())

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
