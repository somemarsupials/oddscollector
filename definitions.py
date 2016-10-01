#!/usr/bin/env python3.5

""" odds.definitions: miscellany used in other modules, such as Premier League
teams, month names and paths to sub-directories and folders.
"""

# file path towards directory for saving HTML
HTML_SUB_PATH = './html'

# database information
DB_SUB_DIR = './data'
DB_SUB_PATH = DB_SUB_DIR + '/odds.sqlite'
DB_BACKUP_SUB_PATH = './data/backup/'

# names of Premier League teams
PL = {
    'arsenal': 'ARS', 'bournemouth': 'BOU', 'burnley': 'BUR',
    'chelsea': 'CHE', 'crystal palace': 'CRY', 'everton': 'EVE',
    'hull': 'HUL', 'leicester': 'LEI', 'liverpool': 'LIV',
    'man city': 'MCI', 'man utd': 'MUN', 'middlesbrough': 'MID',
    'southampton': 'SOU', 'stoke': 'STK', 'sunderland': 'SUN',
    'swansea': 'SWA', 'tottenham': 'TOT', 'watford': 'WAT',
    'west brom': 'WBA', 'west ham': 'WHU'
    }

RESULTS = tuple(PL.keys()) + ('draw',)

# month names
MONTHS = (
    -1, 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
    'september', 'october', 'november', 'december'
    )

# headings for database tables
ROW_HEADINGS = ('ROW', 'ID', 'HOME', 'AWAY', 'TIMESTAMP', 'DATE', 'TIME',
                'ODDS (H)', 'ODDS (D)', 'ODDS (A)','SCORE (H)', 'SCORE (A)',
                'RESULT')
