"""
scrape.py
Author: Brian Boates
"""
from common.database_helper import DatabaseHelper
from scrapers import default_scraper_sets

def update(scraper, seasons=None, pages=range(1, 82)):
    """
    params:
        scraper: Scraper object
        seasons: int/list | season(s) to scrape
        pages: int/list | page(s) to scrape
    """
    print ' | Updating %s' % scraper

    # penalties data in chronological order
    if scraper.get_name() == 'TeamGamePenaltiesScraper':
        pages = range(1, scraper.get_max_page())

    # if seasons and/or pages are integers, convert to lists
    if type(seasons) != type([]):
        seasons = [seasons]
    if type(pages) != type([]):
        pages = [pages]

    database_helper = DatabaseHelper(scraper.get_db())

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
    database_helper = DatabaseHelper(scraper.get_db())
    database_helper.execute_query(scraper.drop_table_query())
    database_helper.execute_query(scraper.create_table_query())
    database_helper.close()

    # all available season (exclude lockout in 2005)
    all_seasons = [str(i) for i in range(1988, 2015) if i != 2005]
    all_pages = range(1, scraper.get_max_page())

    update(scraper, all_seasons, all_pages)


def main():

    # update all scrapers
    scraper_set_key = 'nhl'
    for scraper in default_scraper_sets[scraper_set_key]:
        build_from_scratch(scraper)
#        scraper.silent()
#        update(scraper)


if __name__ == '__main__':
    main()