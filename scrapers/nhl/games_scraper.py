"""
games_scraper.py
Author: Brian Boates
"""
import re
import sha
from common.database_helper import DatabaseHelper
from scrapers.scraper import Scraper
from utils.nhl_utils import *

class GamesScraper(Scraper):
    """
    """
    def __init__(self,
                 season=None,
                 page=None,
                 db='nhl',
                 table='games'):
        super(GamesScraper, self).__init__(season=season,
                                           page=page,
                                           db=db,
                                           table=table)
        self.set_name('GamesScraper')
        self._metadata_columns = ['season', 'page', 'token']
        self.set_column_names(['game_date',
                               'away_team',
                               'away_goals',
                               'home_team',
                               'home_goals',
                               'result',
                               'winning_goaltender',
                               'winning_goal_scorer',
                               'away_shots',
                               'away_powerplay_goals',
                               'away_powerplays',
                               'away_penalty_minutes',
                               'home_shots',
                               'home_powerplay_goals',
                               'home_powerplays',
                               'home_penalty_minutes',
                               'attendance'] \
                                + self._metadata_columns)
        self._num_data_columns = self.get_num_columns() - len(self._metadata_columns)
        self.set_min_season(1988)
        self.set_max_page(45)

    def get_url(self):
        values = (self.get_season(), self.get_page())
        return 'http://www.nhl.com/stats/game?fetchKey=%s2ALLSATAll&viewName=summary&sort=gameDate&gp=1&pg=%s' % values

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
        num_rows = len(parsed_html) / self._num_data_columns # 3 extra columns
        for i in xrange(num_rows):

            row = parsed_html[i*self._num_data_columns:(i+1)*self._num_data_columns]

            # format date as YYYY-MM-DD
            row[0] = format_date(row[0])

            # convert team names to acronyms
            row[1] = format_team_name(row[1])
            row[3] = format_team_name(row[3])

            # fill in empty results with R for regulation
            row[5] = 'R' if row[5] == '' else row[5]

            # generate a unique identifier
            game_str = row[0] + '_' + row[1] + '_' + row[3]
            game_token = sha.new(game_str).hexdigest()

            row = tuple(row + [self.get_season(), self.get_page(), game_token])
            if self.is_verbose():
                print row

            data.append(row)

        return tuple(data)

    def create_table_query(self):
        query  = " CREATE TABLE IF NOT EXISTS %s.%s (" % self.database_table()
        query += " game_date            DATE          \
                 , away_team            VARCHAR(3)    \
                 , away_goals           INT           \
                 , home_team            VARCHAR(3)    \
                 , home_goals           INT           \
                 , result               VARCHAR(2)    \
                 , winning_goaltender   VARCHAR(64)   \
                 , winning_goal_scorer  VARCHAR(64)   \
                 , away_shots           INT           \
                 , away_powerplay_goals INT           \
                 , away_powerplays      INT           \
                 , away_penalty_minutes INT           \
                 , home_shots           INT           \
                 , home_powerplay_goals INT           \
                 , home_powerplays      INT           \
                 , home_penalty_minutes INT           \
                 , attendance           INT           \
                 , season               INT           \
                 , page                 INT           \
                 , token                VARCHAR(255)  \
                 , etl_created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP \
                 , PRIMARY KEY          (game_date, away_team, home_team) \
                 , KEY idx_away_team    (away_team)   \
                 , KEY idx_home_team    (home_team)   \
                 , KEY idx_result       (result)      \
                 , KEY idx_season       (season)      \
                 , KEY idx_page         (page)        \
                 , UNIQUE KEY idx_token (token)       \
                 ) ENGINE=InnoDB DEFAULT CHARSET=utf8 \
                 "
        return query
