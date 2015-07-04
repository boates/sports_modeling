from nhl import GamesScraper
from nhl import TeamGamesScraper
from nhl import TeamGamePenaltiesScraper

nhl_scrapers = [GamesScraper(),
                TeamGamesScraper(),
                TeamGamePenaltiesScraper()]

default_scraper_sets = {'nhl': nhl_scrapers}
