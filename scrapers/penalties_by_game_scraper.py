"""
penalties_by_game_scraper.py
Author: Brian Boates
"""
import sys
sys.dont_write_bytecode = True
import re
from database_helper import DatabaseHelper
from nhl_scraper import NHLScraper
from utils.nhl_utils import *

class PenaltiesByGameScraper(NHLScraper):
    """
    """
    def __init__(self, season=2014, page=1, database_name='nhl', table_name='penalties_by_game'):
        super(PenaltiesByGameScraper, self).__init__(season=season
                                                    ,page=page
                                                    ,database_name=database_name
                                                    ,table_name=table_name)
        self.set_name('PenaltiesByGameScraper')
        self.set_column_names(('game_id'
                              ,'season'
                              ,'game_date'
                              ,'team'
                              ,'opponent'
                              ,'location'
                              ,'minors'
                              ,'majors'
                              ,'misconducts'
                              ,'game_misconducts'
                              ,'match_penalties'
                              ,'bench_minors'
                              ,'total_penalties'
                              ,'penalty_minutes'))
        self.set_max_page(85)

    def get_url(self):
        values = (self.get_season(), self.get_page())
        return 'http://www.nhl.com/ice/gamestats.htm?fetchKey=%s2ALLSATALL&viewName=teamPenaltiesByGame&sort=game.gameDate&pg=%s' % values

    def clean_html(self, html):
        html = html.replace('</td>', '')
        html = html.replace('</a', '')
        html = html.replace('>', '')
        html = html.replace('<', '')
        html = html.replace('.', '')
        html = html.replace('\'', '')
        return html

    def parse_html(self):
        parsed_html = map(self.clean_html, re.findall(r">[\w .,'</>()-]*</td>", self.get_html()))

        # find beginning of actual data by detecting a month name
        keep_looping = True
        while keep_looping:
            try:
                first_item = parsed_html[0].split()[0]
            except IndexError:
                first_item = ''
            if first_item not in months():
                parsed_html = parsed_html[1:]
            else:
                keep_looping = False

        data = []
        num_rows = len(parsed_html) / (self.get_num_columns()-2) # 4 extra columns
        for i in xrange(num_rows):

            row = parsed_html[i*(self.get_num_columns()-2):(i+1)*(self.get_num_columns()-2)]

            # format date as YYYY-MM-DD
            row[0] = format_date(row[0])

            # convert team names to acronyms
            row[1] = format_team_name(row[1])
            row[2] = format_team_name(row[2])

            # fill in empty results with R for regulation
            row[3] = 'HOME' if row[3] == 'H' else 'AWAY'

            if row[3] == 'HOME':
                home_team = row[1]
                away_team = row[2]
            else:
                away_team = row[1]
                home_team = row[2]

            game_id = row[0] + '_' + away_team + '_' + home_team

            row = tuple([game_id, str(self.get_season())] + row)
            if self.is_verbose():
                print row

            data.append(row)

        return tuple(data)

    def create_table_query(self):
        query  = " CREATE TABLE IF NOT EXISTS %s.%s (" % self.database_table()
        query += " game_id VARCHAR(32)           \
                 , season SMALLINT(4)            \
                 , game_date DATE                \
                 , team VARCHAR(3)               \
                 , opponent VARCHAR(3)           \
                 , location VARCHAR(4)           \
                 , minors SMALLINT(4)            \
                 , majors SMALLINT(4)            \
                 , misconducts SMALLINT(4)       \
                 , game_misconducts SMALLINT(4)  \
                 , match_penalties SMALLINT(4)   \
                 , bench_minors SMALLINT(4)      \
                 , total_penalties SMALLINT(4)   \
                 , penalty_minutes SMALLINT(4)   \
                 , PRIMARY KEY (game_date, team) \
                 , KEY (game_id)                 \
                 , KEY (season)                  \
                 , KEY (opponent)                \
                 , KEY (location))               \
                 "
        return query


def update(seasons, pages):

    if type(seasons) != type([]):
        seasons = [seasons]
    if type(pages) != type([]):
        pages = [pages]

    database_helper = DatabaseHelper()

    for season in seasons:
        for page in pages:

            print 'season: %s; page: %s' % (season, page)

            penalties_by_game_scraper = PenaltiesByGameScraper(season=season, page=page)
            query = penalties_by_game_scraper.replace_into_query()
            database_helper.execute_query(query)

    database_helper.close()


def build_from_scratch():

    database_helper = DatabaseHelper()

    penalties_by_game_scraper = PenaltiesByGameScraper()
    database_helper.execute_query(penalties_by_game_scraper.drop_table_query())
    database_helper.execute_query(penalties_by_game_scraper.create_table_query())

    database_helper.close()

    all_seasons = [str(i) for i in range(1988, 2015) if i != 2005]
    all_pages = range(1, 85)

    update(all_seasons, all_pages)


def main():

    update(2014, [1, 2, 3])


if __name__ == '__main__':
    main()
