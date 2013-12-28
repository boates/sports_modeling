"""
game_by_game_scraper.py
Author: Brian Boates
"""
import sys
sys.dont_write_bytecode = True
import re
from database_helper import DatabaseHelper
from nhl_scraper import NHLScraper
from utils.nhl_utils import *

class GameByGameScraper(NHLScraper):
    """
    """
    def __init__(self, season=2014, page=1, database_name='nhl', table_name='game_by_game'):
        super(GameByGameScraper, self).__init__(season=season
                                               ,page=page
                                               ,database_name=database_name
                                               ,table_name=table_name)
        self.set_name('GameByGameScraper')
        self.set_column_names(('game_id'
                              ,'season'
                              ,'game_date'
                              ,'team'
                              ,'decision'
                              ,'result'
                              ,'location'
                              ,'opponent'
                              ,'record'
                              ,'wins'
                              ,'losses'
                              ,'goals_for'
                              ,'goals_against'
                              ,'scorers'
                              ,'powerplay_goals'
                              ,'powerplay_opportunities'
                              ,'powerplay_goals_against'
                              ,'times_shorthanded'
                              ,'shots_for'
                              ,'shots_against'
                              ,'winning_goaltender'
                              ,'attendance'))
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

            # use None if there are no scorers given
            row[9] = 'NULL' if row[9] == '' else row[9]

            # remove comma in attendance
            row[17] = row[17].replace(',','')

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

            game_id = row[0] + '_' + away_team + '_' + home_team

            row = tuple([game_id, str(self.get_season())] + row)
            if self.is_verbose():
                print row

            data.append(row)

        return tuple(data)

    def create_table_query(self):
        query  = " CREATE TABLE IF NOT EXISTS %s.%s (" % self.database_table()
        query += " game_id VARCHAR(32)                 \
                 , game_date DATE                      \
                 , season SMALLINT(4)                  \
                 , team VARCHAR(3)                     \
                 , decision VARCHAR(2)                 \
                 , result VARCHAR(2)                   \
                 , location VARCHAR(4)                 \
                 , opponent VARCHAR(3)                 \
                 , record VARCHAR(16)                  \
                 , wins SMALLINT(4)                    \
                 , losses SMALLINT(4)                  \
                 , goals_for SMALLINT(4)               \
                 , goals_against SMALLINT(4)           \
                 , scorers VARCHAR(128)                \
                 , powerplay_goals SMALLINT(4)         \
                 , powerplay_opportunities SMALLINT(4) \
                 , powerplay_goals_against SMALLINT(4) \
                 , times_shorthanded SMALLINT(4)       \
                 , shots_for SMALLINT(4)               \
                 , shots_against SMALLINT(4)           \
                 , winning_goaltender VARCHAR(64)      \
                 , attendance INT(11)                  \
                 , PRIMARY KEY (game_date, team)       \
                 , KEY (game_id)                       \
                 , KEY (season)                        \
                 , KEY (decision)                      \
                 , KEY (result)                        \
                 , KEY (location)                      \
                 , KEY (opponent))                     \
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

            game_by_game_scraper = GameByGameScraper(season=season, page=page)
            query = game_by_game_scraper.replace_into_query()
            database_helper.execute_query(query)

    database_helper.close()


def build_from_scratch():

    database_helper = DatabaseHelper()

    game_by_game_scraper = GameByGameScraper()
    database_helper.execute_query(game_by_game_scraper.drop_table_query())
    database_helper.execute_query(game_by_game_scraper.create_table_query())

    database_helper.close()

    all_seasons = [str(i) for i in range(1988, 2015) if i != 2005]
    all_pages = range(1, 85)

    update(all_seasons, all_pages)


def main():

    update(2014, [1, 2, 3])


if __name__ == '__main__':
    main()
