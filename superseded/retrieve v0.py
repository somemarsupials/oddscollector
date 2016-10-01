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
from definitions import HTML_SUB_PATH, PL

# CONSTANTS
ODDSCHECKER = 'http://www.oddschecker.com/football/english/premier-league'
BBC_FIXT = 'http://www.bbc.co.uk/sport/football/premier-league/fixtures'
BBC_RESU = 'http://www.bbc.co.uk/sport/football/premier-league/results'

# FUNCTIONS


def _save_html(html, source='unnamed'):
    """ Save HTML retrieved from a webpage as a .html file.
    """
    # create HTML directory if non-existent
    if not os.path.isdir(HTML_SUB_PATH):
        os.mkdir(HTML_SUB_PATH)
    # name for HTML text file
    path = HTML_SUB_PATH + '/' + source + str(datetime.date.today()) + '.xml'
    try:
        with open(path, 'w') as target:
            target.write(str(html.content))
        return path
    except FileNotFoundError:
        print('HTML file could not be saved at: {}'.format(path))


def _get_content(url, save_under_name=None):
    """ Convert HTML into an etree, and optionally save the HTML.
    """
    page = requests.get(url)
    tree = html.fromstring(page.content)
    if save_under_name:
        try:
            path = _save_html(page, save_under_name)
        except FileNotFoundError:
            pass # error message printed as part of function
    return tree


def get_fixtures(url=BBC_FIXT):
    """ Get fixture information (home, away, gameweek date) from a URL.
    Designed to work exclusively with the BBC Fixtures webpage. Return a list
    of Fixture objects with this information.
    """
    tree = _get_content(url)
    # read home and away teams
    try:
        home_teams = tree.xpath('//span[@class="team-home teams"]/a/text()')
    except XPathEvalError:
        print('Home teams could not be accessed from {}'.format(url))
        raise
    except IndexError:
        print('Not enough home teams found from: {}'.format(url))
        raise
    try:
        away_teams = tree.xpath('//span[@class="team-away teams"]/a/text()')
    except XPathEvalError:
        print('Away teams could not be accessed from: {}'.format(url))
        raise
    except IndexError:
        print('Not enough away teams found from: {}'.format(url))
        raise
    # create Fixture objects to hold data
    # checking of team names is done during Fixture creation
    fixtures = []
    try:
        for num in range(len(home_teams)):
            fixtures.append(Fixture(home_teams[num], away_teams[num]))
    except IndexError:
        print('Mismatching home and away teams')
        print('Home teams: {}'.format(len(home_teams)))
        print('Away teams: {}'.format(len(away_teams)))
        raise
    return fixtures


def get_odds(url=ODDSCHECKER, fixtures=None):
    """ Get data from a URL about the teams playing and the corresponding
    odds. Designed to work exlusively with the Oddschecker website. If the
    fixture parameter is given, updates a list of Fixtures and returns.
    Otherwise, creates a list of Fixtures and returns.
    """
    tree = _get_content(url, 'oddschecker')
    # read teams, in order of the odds given, from webpage
    teams = tree.xpath('//span[@class="fixtures-bet-name"]/text()')
    # expect three results for every two teams, counting draw_odds
    # reduce the list to the current gameweek; 30 odds assuming 20 teams
    if len(teams) < 1.5*len(PL):
        print(teams)
        raise ValueError('Not enough results found: {}'.format(len(teams)))
    # read odds
    odds = tree.xpath('//span[@class="odds"]/text()')
    if len(odds) < 1.5*len(PL):
        print(teams)
        raise ValueError('Not enough odds found: {}'.format(len(teams)))
    results = []
    if fixtures: # update Fixture objects if they exist
        for num in range(0, len(teams), 3):
            home, away = teams[num], teams[num+2]
            for f in fixtures: # find the right Fixture to update
                if f.uid == Fixture.create_uid(home, away):
                    f.set_odds(odds[num], odds[num+1], odds[num+2])
                    results.append(f)
        for f in fixtures:
            found = False
            for r in results:
                if f.uid == r.uid:
                    found = True
            if not found:
                results.append(f)
    else: # otherwise create Fixture objects
        for num in range(0, len(teams), 3):
            new = Fixture(teams[num], teams[num+2])
            new.set_odds(odds[num], odds[num+1], odds[num+2])
            results.append(new)
    return results


def get_results(url=BBC_RESU, fixtures=None):
    """ Get results data (scores) from the BBC Results page. Designed to work
    exclusively with the BBC Results page. If the fixture parameter is given,
    updates a list of Fixtures and returns. Otherwise, creates a list of
    Fixtures and returns.
    """
    # >>> only designed to work with the BBC! <<<
    tree = _get_content(url, 'bbc')
    # read teams, in order of the fixtures given, from webpage
    home_teams = tree.xpath('//span[@class="team-home teams"]/a/text()')
    if len(home_teams) < len(PL)/2:
        print(home_teams)
        raise ValueError('Too few home teams: {}'.format(len(home_teams)))
    away_teams = tree.xpath('//span[@class="team-away teams"]/a/text()')
    if len(away_teams) < len(PL)/2:
        print(away_teams)
        raise ValueError('Too few away teams: {}'.format(len(away_teams)))
    # read scores
    scores = tree.xpath('//abbr[@title="Score"]/text()')
    if len(scores) < len(PL)/2:
        print(scores)
        raise ValueError('Too few results: {}'.format(len(scores)))
    # check that results match up
    if not len(home_teams) == len(away_teams) == len(scores):
        error = (
            'Numbers of teams and scores do not match: {0} home, {1} away, '
            '{3} scores'.format(len(home_teams), len(away_teams), len(scores))
            )
        raise ValueError(error)
    # assemble fixtures from data
    results = []
    if fixtures: # update Fixture objects if given
        for num in range(len(home_teams)): # all lists are the same length
            home = home_teams[num]
            for f in fixtures: # ensure the correct fixture is updated
                if f.home == home:
                    f.set_result(scores[num])
    else: # else create Fixture objects from results
        for num in range(len(home_teams)):
            new = Fixture(home_teams[num], away_teams[num])
            new.set_result(scores[num])
            results.append(new)
    return results
