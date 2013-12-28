"""
nhl_scraper.py
Author: Brian Boates
"""
import sys
sys.dont_write_bytecode = True
import urllib2

class NHLScraper(object):
    """
    """
    def __init__(self, season=None, page=None, database_name=None, table_name=None):
        self._name = 'NHLScraper'
        self._season = season
        self._page = page
        self._database_name = database_name
        self._table_name = table_name
        self._column_names = ()
        self._html = None
        self._data = None
        self._max_page = None
        self._verbose = True

    def __str__(self):
        s  = '<%s: ' % self.get_name()
        s += 'season=%s, ' % self.get_season()
        s += 'page=%s, ' % self.get_page()
        s += 'database_name=%s, ' % self.get_database_name()
        s += 'table_name=%s>' % self.get_table_name()
        return s

    def __repr__(self):
        return self.__str__()

    def get_name(self):
        return self._name

    def get_column_names(self):
        return self._column_names

    def get_num_columns(self):
        return len(self._column_names)

    def get_num_rows(self):
        return len(self.get_data())

    def get_season(self):
        return self._season

    def get_page(self):
        return self._page

    def get_max_page(self):
        return self._max_page

    def get_database_name(self):
        return self._database_name

    def get_table_name(self):
        return self._table_name

    def database_table(self):
        return (self.get_database_name(), self.get_table_name())

    def set_name(self, name):
        self._name = name

    def set_column_names(self, column_names):
        self._column_names = column_names

    def set_season(self, season):
        self._season = season
        self._data = None

    def set_page(self, page):
        self._page = page
        self._data = None

    def set_max_page(self, max_page):
        self._max_page = max_page

    def set_database_name(self, database_name):
        self._database_name = database_name

    def set_table_name(self, table_name):
        self._table_name = table_name

    def verbose(self):
        self._verbose = True

    def silent(self):
        self._verbose = False

    def is_verbose(self):
        return self._verbose

    def get_url(self):
        raise NotImplementedError, 'must be implemented in sub-class'

    def get_html(self):
        if not self._html:
            self._html = urllib2.urlopen(self.get_url()).read()
        return self._html

    def clean_html(self):
        raise NotImplementedError, 'must be implemented in sub-class'

    def parse_html(self):
        raise NotImplementedError, 'must be implemented in sub-class'

    def get_data(self):
        if not self._data:
            self._data = self.parse_html()
        return self._data

    def create_table_query(self):
        raise NotImplementedError, 'must be implemented in sub-class'

    def drop_table_query(self):
        return "DROP TABLE IF EXISTS %s.%s" % self.database_table()

    def replace_into_query(self):
        data = self.get_data()
        queries = []
        query  = "REPLACE INTO %s.%s (" % self.database_table()
        query += "%s, "*self.get_num_columns() % self.get_column_names()
        query  = query[:-2] + ") "
        query += "VALUES"
        query += "%s, "*self.get_num_rows() % tuple([repr(row) for row in data])
        query  = query[:-2]
        return query


def main():
    nhl_scraper = NHLScraper()
    nhl_scraper.get_html('http://www.nhl.com')


if __name__ == '__main__':
    main()
