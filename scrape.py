"""
scrape.py
Author: Brian Boates
"""
from datetime import date
from common.database_helper import DatabaseHelper
from scrapers import default_scraper_sets

def update(scraper, rebuild=False):
    """
    Updates all pages for current and future seasons

    params:
        scraper: Scraper object
        seasons: int/list | season(s) to scrape
    """
    print ' | Updating %s' % scraper

    database_helper = DatabaseHelper(scraper.get_db())

    if rebuild:
        database_helper.execute_query(scraper.drop_table_query())
    database_helper.execute_query(scraper.create_table_query())

    season_start_query = """SELECT MAX(season) FROM %s.%s""" % scraper.database_table()
    season_start = database_helper.get_query_results(season_start_query)[0][0]
    if not season_start:
        season_start = scraper.get_min_season()
    season_end = date.today().year + 1
    seasons = [i for i in range(season_start, season_end) if i != 2005] # 2005 lockout

    pages = range(1, scraper.get_max_page())

    for season in seasons:
        for page in pages:

            print ' |   season: %s; page: %s' % (season, page)

            scraper.set_season(season)
            scraper.set_page(page)
            query = scraper.replace_into_query()
            database_helper.execute_query(query)

    database_helper.close()


def main():

    # update all scrapers
    scraper_set_key = 'nhl'
    for scraper in default_scraper_sets[scraper_set_key]:
        scraper.silent()
        update(scraper)


if __name__ == '__main__':
    main()
