"""
game_summary_scraper.py
Author: Brian Boates
"""
import sys
sys.dont_write_bytecode = True
import re
from database_helper import DatabaseHelper
from nhl_scraper import NHLScraper
from utils.nhl_utils import *

class GameSummaryScraper(NHLScraper):
    """
    """
    def __init__(self, season=2014, page=1, database_name='nhl', table_name='game_summaries'):
        super(GameSummaryScraper, self).__init__(season=season
                                                ,page=page
                                                ,database_name=database_name
                                                ,table_name=table_name)
        self.set_name('GameSummaryScraper')
        self.set_column_names(('id'
                              ,'season'
                              ,'game_date'
                              ,'away_team'
                              ,'away_goals'
                              ,'home_team'
                              ,'home_goals'
                              ,'result'
                              ,'winning_goaltender'
                              ,'winning_goal_scorer'
                              ,'away_shots'
                              ,'away_powerplay_goals'
                              ,'away_powerplays'
                              ,'away_penalty_minutes'
                              ,'home_shots'
                              ,'home_powerplay_goals'
                              ,'home_powerplays'
                              ,'home_penalty_minutes'
                              ,'attendance'))
        self.set_max_page(45)

    def get_url(self):
        values = (self.get_season(), self.get_page())
        return 'http://www.nhl.com/ice/gamestats.htm?fetchKey=%s2ALLSATALL&viewName=summary&sort=gameDate&pg=%s' % values

    def clean_html(self, html):
        html = html.replace('</td>', '')
        html = html.replace('</a', '')
        html = html.replace('>', '')
        html = html.replace('<', '')
        html = html.replace('.', '')
        html = html.replace(',', '')
        html = html.replace('\'', '')
        return html

    def parse_html(self):
        parsed_html = map(self.clean_html, re.findall(r">[\w .,'</>()]*</td>", self.get_html()))

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
        num_rows = len(parsed_html) / (self.get_num_columns()-2) # 2 extra columns
        for i in xrange(num_rows):

            row = parsed_html[i*(self.get_num_columns()-2):(i+1)*(self.get_num_columns()-2)]

            # format date as YYYY-MM-DD
            row[0] = format_date(row[0])

            # convert team names to acronyms
            row[1] = format_team_name(row[1])
            row[3] = format_team_name(row[3])

            # fill in empty results with R for regulation
            row[5] = 'R' if row[5] == '' else row[5]

            game_id = row[0] + '_' + row[1] + '_' + row[3]

            row = tuple([game_id, str(self.get_season())] + row)
            if self.is_verbose():
                print row

            data.append(row)

        return tuple(data)

    def create_table_query(self):
        query  = " CREATE TABLE IF NOT EXISTS %s.%s (" % self.database_table()
        query += " id VARCHAR(32)                   \
                 , season SMALLINT(4)               \
                 , game_date DATE                   \
                 , away_team VARCHAR(3)             \
                 , away_goals SMALLINT(4)           \
                 , home_team VARCHAR(3)             \
                 , home_goals SMALLINT(4)           \
                 , result VARCHAR(2)                \
                 , winning_goaltender VARCHAR(64)   \
                 , winning_goal_scorer VARCHAR(64)  \
                 , away_shots SMALLINT(4)           \
                 , away_powerplay_goals SMALLINT(4) \
                 , away_powerplays SMALLINT(4)      \
                 , away_penalty_minutes SMALLINT(4) \
                 , home_shots SMALLINT(4)           \
                 , home_powerplay_goals SMALLINT(4) \
                 , home_powerplays SMALLINT(4)      \
                 , home_penalty_minutes SMALLINT(4) \
                 , attendance INT(11)               \
                 , PRIMARY KEY (id)                 \
                 , KEY (game_date)                  \
                 , KEY (away_team)                  \
                 , KEY (home_team))                 \
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

            game_summary_scraper = GameSummaryScraper(season=season, page=page)
            query = game_summary_scraper.replace_into_query()
            database_helper.execute_query(query)

    database_helper.close()


def build_from_scratch():

    database_helper = DatabaseHelper()

    game_summary_scraper = GameSummaryScraper()
    database_helper.execute_query(game_summary_scraper.drop_table_query())
    database_helper.execute_query(game_summary_scraper.create_table_query())

    database_helper.close()

    all_seasons = [str(i) for i in range(1988, 2015) if i != 2005]
    all_pages = range(1, 45)

    update(all_seasons, all_pages)


def main():

    update(2014, [1, 2, 3])


if __name__ == '__main__':
    main()
