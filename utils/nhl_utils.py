"""
nhl_utils.py
Author: Brian Boates
"""
def months():
    return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'
           ,'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def team_name_map():
    return {'ANAHEIM': 'ANA'
           ,'ATLANTA': 'ATL'
           ,'BOSTON': 'BOS'
           ,'BUFFALO': 'BUF'
           ,'CALGARY': 'CGY'
           ,'CAROLINA': 'CAR'
           ,'CHICAGO': 'CHI'
           ,'COLORADO': 'COL'
           ,'COLUMBUS': 'CBJ'
           ,'DALLAS': 'DAL'
           ,'DETROIT': 'DET'
           ,'EDMONTON': 'EDM'
           ,'FLORIDA': 'FLA'
           ,'HARTFORD': 'HFD'
           ,'LOS ANGELES': 'LAK'
           ,'MINNESOTA': 'MIN'
           ,'MONTREAL': 'MTL'
           ,'NASHVILLE': 'NSH'
           ,'NEW JERSEY': 'NJD'
           ,'NY ISLANDERS': 'NYI'
           ,'NY RANGERS': 'NYR'
           ,'OTTAWA': 'OTT'
           ,'PHILADELPHIA': 'PHI'
           ,'PHOENIX': 'PHX'
           ,'PITTSBURGH': 'PIT'
           ,'QUEBEC': 'QBC'
           ,'ST LOUIS': 'STL'
           ,'SAN JOSE': 'SJS'
           ,'TAMPA BAY': 'TBL'
           ,'TORONTO': 'TOR'
           ,'VANCOUVER': 'VAN'
           ,'WASHINGTON': 'WSH'
           ,'WINNIPEG': 'WPG'
           ,'Winnipeg Jets (1979)': 'WPG'
           ,'WIN': 'WPG'
           ,'QUE': 'QBC'
           ,'MNS': 'MIN'}

def valid_team_names():
    return team_name_map().values()

def format_team_name(team_name):
    return team_name_map()[team_name]

def format_date(date):
    month_name_map = {'Jan': '01'
                     ,'Feb': '02'
                     ,'Mar': '03'
                     ,'Apr': '04'
                     ,'May': '05'
                     ,'Jun': '06'
                     ,'Jul': '07'
                     ,'Aug': '08'
                     ,'Sep': '09'
                     ,'Oct': '10'
                     ,'Nov': '11'
                     ,'Dec': '12'}

    year = date.split()[2]
    if int(year) > 50:
        year = '19' + year
    else:
        year = '20' + year
    month = month_name_map[date.split()[0]]
    day = date.split()[1]

    return year + '-' + month + '-' + day
