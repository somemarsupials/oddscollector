#!/usr/bin/env python3.5

""" retrieve: functions to retrieve fixture and odds information from
dedicated websites.
"""

# built in modules
import os
import os.path
import requests
import datetime

# third-party modules
from lxml import html
from lxml.etree import XPathEvalError

# package modules
from fixture import Fixture
from parser import BBCParser
from definitions import HTML_SUB_PATH, PL

# CONSTANTS
ODDSCHECKER = 'http://www.oddschecker.com/football/english/premier-league'
BBC_FIXT = 'http://www.bbc.co.uk/sport/football/premier-league/fixtures'
BBC_RESU = 'http://www.bbc.co.uk/sport/football/premier-league/results'
                
# FUNCTIONS


def get_fixtures(url=BBC_FIXT):
    """ Get fixture information (home, away, gameweek date) from a URL.
    Designed to work exclusively with the BBC Fixtures webpage. Return a list
    of Fixture objects with this information.
    """
    p = BBCParser()
    p.feed(requests.get(url).text)
    p.run_checks()
    fixtures = [] # error checking is done during Fixture creation
    matches = zip(p.home, p.away, p.dates, p.ko)
    for item in matches:
        f = Fixture(item[0], item[1])
        f.set_date(item[2])
        f.set_time(item[3])
        fixtures.append(f)
    return fixtures


def get_odds(url=ODDSCHECKER, fixtures=None):
    """ Get data from a URL about the teams playing and the corresponding
    odds. Designed to work exlusively with the Oddschecker website. If the
    fixture parameter is given, updates a list of Fixtures and returns.
    Otherwise, creates a list of Fixtures and returns.
    """
    page = requests.get(url)
    tree = html.fromstring(page.content)
    # read teams, in order of the odds given, from webpage
    teams = tree.xpath('//span[@class="fixtures-bet-name"]/text()')
    # expect three results for every two teams, counting draw_odds
    if len(teams) < 1.5*len(PL):
        raise ValueError('Not enough results found: {}'.format(len(teams)))
    odds = tree.xpath('//span[@class="odds"]/text()') # read odds
    if len(odds) < len(teams):
        raise ValueError('Not enough odds found: {}'.format(len(teams)))
    if fixtures: # update Fixture objects if they exist
        for num in range(0, len(teams), 3):
            home, away = teams[num], teams[num+2]
            for f in fixtures: # find the right Fixture to update
                if f.home == home and f.away == away:
                    f.set_odds(odds[num], odds[num+1], odds[num+2])
                    fixtures[int(num/3)] = f
    else: # otherwise create Fixture objects
        fixtures = []
        for num in range(0, len(teams), 3):
            new = Fixture(teams[num], teams[num+2])
            new.set_odds(odds[num], odds[num+1], odds[num+2])
            fixtures.append(new)
    return fixtures


def get_results(url=BBC_RESU):
    """ Get results data (scores) from the BBC Results page. Designed to work
    exclusively with the BBC Results page. If the fixture parameter is given,
    updates a list of Fixtures and returns. Otherwise, creates a list of
    Fixtures and returns.
    """
    p = BBCParser()
    p.feed(requests.get(url).text)
    p.run_checks()
    fixtures = [] # error checking is done during Fixture creation
    matches = zip(p.home, p.away, p.dates, p.scores)
    for item in matches:
        f = Fixture(item[0], item[1])
        f.set_date(item[2])
        f.set_result(item[3])
        fixtures.append(f)
    return fixtures   
