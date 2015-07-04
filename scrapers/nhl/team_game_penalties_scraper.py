"""
team_game_penalties_scraper.py
Author: Brian Boates
"""
import re
import sha
from common.database_helper import DatabaseHelper
from scrapers.scraper import Scraper
from utils.nhl_utils import *

class TeamGamePenaltiesScraper(Scraper):
    """
    """
    def __init__(self,
                 season=None,
                 page=None,
                 db='nhl',
                 table='team_game_penalties'):
        super(TeamGamePenaltiesScraper, self).__init__(season=season,
                                                       page=page,
                                                       db=db,
                                                       table=table)
        self.set_name('TeamGamePenaltiesScraper')
        self.set_column_names(('team_game_token',
                               'game_token',
                               'season',
                               'game_date',
                               'team',
                               'opponent',
                               'location',
                               'minors',
                               'majors',
                               'misconducts',
                               'game_misconducts',
                               'match_penalties',
                               'bench_minors',
                               'total_penalties',
                               'penalty_minutes'))
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

            team_game_str = row[0] + '_' + row[1]
            team_game_token = sha.new(team_game_str).hexdigest()

            game_str = row[0] + '_' + away_team + '_' + home_team
            game_token = sha.new(game_str).hexdigest()

            row = tuple([team_game_token, game_token, str(self.get_season())] + row)
            if self.is_verbose():
                print row

            data.append(row)

        return tuple(data)

    def create_table_query(self):
        query  = " CREATE TABLE IF NOT EXISTS %s.%s (" % self.database_table()
        query += " team_game_token    VARCHAR(255)      \
                 , game_token         VARCHAR(255)      \
                 , season             INT               \
                 , game_date          DATE              \
                 , team               VARCHAR(3)        \
                 , opponent           VARCHAR(3)        \
                 , location           VARCHAR(4)        \
                 , minors             INT               \
                 , majors             INT               \
                 , misconducts        INT               \
                 , game_misconducts   INT               \
                 , match_penalties    INT               \
                 , bench_minors       INT               \
                 , total_penalties    INT               \
                 , penalty_minutes    INT               \
                 , etl_created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP \
                 , PRIMARY KEY        (team_game_token) \
                 , KEY idx_game_token (game_token)      \
                 , KEY idx_season     (season)          \
                 , KEY idx_game_date  (game_date)       \
                 , KEY idx_team       (team)            \
                 , KEY idx_opponent   (opponent)        \
                 , KEY idx_location   (location)        \
                 ) ENGINE=InnoDB DEFAULT CHARSET=utf8   \
                 "
        return query
