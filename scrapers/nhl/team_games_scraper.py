"""
team_games_scraper.py
Author: Brian Boates
"""
import re
import sha
from common.database_helper import DatabaseHelper
from scrapers.scraper import Scraper
from utils.nhl_utils import *

class TeamGamesScraper(Scraper):
    """
    """
    def __init__(self,
                 season=None,
                 page=None,
                 db='nhl',
                 table='team_games'):
        super(TeamGamesScraper, self).__init__(season=season,
                                               page=page,
                                               db=db,
                                               table=table)
        self.set_name('TeamGamesScraper')
        self.set_column_names(('token',
                               'game_token',
                               'season',
                               'game_date',
                               'team',
                               'decision',
                               'result',
                               'location',
                               'opponent',
                               'record',
                               'wins',
                               'losses',
                               'goals_for',
                               'goals_against',
                               'scorers',
                               'powerplay_goals',
                               'powerplay_opportunities',
                               'powerplay_goals_against',
                               'times_shorthanded',
                               'shots_for',
                               'shots_against',
                               'winning_goaltender',
                               'attendance'))
        self.set_max_page(85)

    def get_url(self):
        values = (self.get_season(), self.get_page())
        return 'http://www.nhl.com/ice/gamestats.htm?fetchKey=%s2ALLSATALL&viewName=gameSummary&sort=game.gameDate&pg=%s' % values

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
        num_rows = len(parsed_html) / (self.get_num_columns()-4) # 4 extra columns
        for i in xrange(num_rows):

            row = parsed_html[i*(self.get_num_columns()-4):(i+1)*(self.get_num_columns()-4)]

            # format date as YYYY-MM-DD
            row[0] = format_date(row[0])

            # convert team names to acronyms
            row[1] = format_team_name(row[1])
            if row[5] not in valid_team_names():
                row[5] = format_team_name(row[5])

            # fill in empty results with R for regulation
            row[3] = 'R' if row[3] == '' else row[3]

            # fill in empty results with R for regulation
            row[4] = 'HOME' if row[4] == 'H' else 'AWAY'

            # NULL if there are no scorers given
            row[9] = 'NULL' if row[9] == '' else row[9]

            # remove commas in attendance
            row[17] = row[17].replace(',', '')

            # wins and losses
            wins = row[6].split('-')[0]
            losses = row[6].split('-')[1]

            row = row[:7] + [wins, losses] + row[7:]

            if row[4] == 'HOME':
                home_team = row[1]
                away_team = row[5]
            else:
                away_team = row[1]
                home_team = row[5]

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
        query += " token                   VARCHAR(255)      \
                 , game_token              VARCHAR(255)      \
                 , game_date               DATE              \
                 , season                  INT               \
                 , team                    VARCHAR(3)        \
                 , decision                VARCHAR(2)        \
                 , result                  VARCHAR(2)        \
                 , location                VARCHAR(4)        \
                 , opponent                VARCHAR(3)        \
                 , record                  VARCHAR(255)      \
                 , wins                    INT               \
                 , losses                  INT               \
                 , goals_for               INT               \
                 , goals_against           INT               \
                 , scorers                 VARCHAR(255)      \
                 , powerplay_goals         INT               \
                 , powerplay_opportunities INT               \
                 , powerplay_goals_against INT               \
                 , times_shorthanded       INT               \
                 , shots_for               INT               \
                 , shots_against           INT               \
                 , winning_goaltender      VARCHAR(255)      \
                 , attendance              INT               \
                 , etl_created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP \
                 , PRIMARY KEY             (team_game_token) \
                 , KEY idx_game_token      (game_token)      \
                 , KEY idx_game_date       (game_date)       \
                 , KEY idx_season          (season)          \
                 , KEY idx_team            (team)            \
                 , KEY idx_decision        (decision)        \
                 , KEY idx_result          (result)          \
                 , KEY idx_location        (location)        \
                 , KEY idx_opponent        (opponent)        \
                 ) ENGINE=InnoDB DEFAULT CHARSET=utf8        \
                 "
        return query
