"""
scrape.py
Author: Brian Boates
"""
import sys
sys.dont_write_bytecode = True
from common.database_helper import DatabaseHelper
from game_summary_scraper import GameSummaryScraper
from game_by_game_scraper import GameByGameScraper
from penalties_by_game_scraper import PenaltiesByGameScraper

SCRAPERS = [GameSummaryScraper(database_name='nhl', table_name='game_summaries')
           ,GameByGameScraper(database_name='nhl', table_name='game_by_game')
           ,PenaltiesByGameScraper(database_name='nhl', table_name='penalties_by_game')]


def update(scraper, seasons=[2014], pages=[1,2,3]):
    """
    params:
        scraper: [...]Scraper object
        seasons: int/list | season(s) to scrape
        pages: int/list | page(s) to scrape
    """
    print ' | Updating %s' % scraper

    # if seasons and/or pages are integers, convert to lists
    if type(seasons) != type([]):
        seasons = [seasons]
    if type(pages) != type([]):
        pages = [pages]

    database_helper = DatabaseHelper(scraper.get_database_name())

    for season in seasons:
        for page in pages:

            print ' |  season: %s; page: %s' % (season, page)

            scraper.set_season(season)
            scraper.set_page(page)
            query = scraper.replace_into_query()
            database_helper.execute_query(query)

    database_helper.close()


def build_from_scratch(scraper):
    """
    params:
        scraper: [...]Scraper object
    """
    # blast entire table and re-create
    database_helper = DatabaseHelper(scraper.get_database_name())
    database_helper.execute_query(scraper.drop_table_query())
    database_helper.execute_query(scraper.create_table_query())
    database_helper.close()

    # all available season (exclude lockout in 2005)
    all_seasons = [str(i) for i in range(1988, 2015) if i != 2005]
    all_pages = range(1, scraper.get_max_page())

    update(all_seasons, all_pages)


def main():

    # update all scrapers
    for scraper in SCRAPERS:
        scraper.silent()
        update(scraper)


if __name__ == '__main__':
    main()
