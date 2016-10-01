#!/usr/bin/env python3.5

""" fixture: a class to store data about fixtures
"""

# built-in modules
import requests
import datetime

# package modules
from definitions import PL, MONTHS

# CONSTANTS
_ODDS_DP = 5

# CLASSES


class Fixture:

    def __init__(self, home, away):
        """ A class to validate and store information about a fixture. Only
        requires the home and away teams; the date, odds and result are all
        handled in other functions.
        """
        # check teams in Premier League
        if home.lower() in PL:
            self.home = home
        else:
            error = 'Home team ({}) not recognised'.format(home)
            raise ValueError(error)
        if away.lower() in PL:
            self.away = away
        else:
            error = 'Away team ({}) not recognised'.format(away)
            raise ValueError(error)
        # unique fixture identifier
        self.uid = Fixture.create_uid(home, away)
        # time stamp
        self.stamp = str(datetime.date.today())

    # methods for adding new data

    def set_odds(self, home, draw, away):
        """ Convert string-based fractional odds to decimals and store as
        attributes. Assumes odds come from Oddschecker.
        """
        self.home_odds = self._frac_to_dec(home)
        self.draw_odds = self._frac_to_dec(draw)
        self.away_odds = self._frac_to_dec(away)
        return self

    def set_date(self, date):
        """ Add a date to the fixture. Assumes dates come from the BBC
        Fixtures webpage.
        """
        self.date = self._text_to_date(date)
        self.uid = Fixture.create_uid(self.home, self.away, self.date.year)

    def set_time(self, time):
        """ Add a time to the fixture. Assumes times come from the BBC
        Fixtures webpage.
        """
        self.time = self._text_to_time(time)

    def set_result(self, score):
        """ Assign result information to the fixture.
        """
        self.home_score, self.away_score = self._text_to_scores(score)
        if self.home_score == self.away_score:
            self.result = 'D'
        elif self.home_score > self.away_score:
            self.result = 'H'
        else:
            self.result = 'A'
        return self

    # methods for returning attributes in a fixed order
    
    def basic_info(self):
        """ Basic information for database.
        """
        return (self.uid, self.home, self.away, self.stamp)

    def odds_info(self):
        """ Odds information for database.
        """
        try:
            return (self.home_odds, self.draw_odds, self.away_odds)
        except AttributeError:
            raise

    def time_info(self):
        try:
            return (str(self.date), str(self.time))
        except AttributeError:
            raise

    def result_info(self):
        """ Score information for database.
        """
        try:
            return (self.home_score, self.away_score, self.result)
        except AttributeError:
            raise

    # other methods
    def __repr__(self):
        return '<class Fixture: {0} vs. {1}>'.format(self.home, self.away)

    @classmethod
    def create_uid(cls, home, away, year=None):
        """ Combine two team names into an identifier.
        """
        sep = '-'
        f = lambda team: team.lower()
        uid = PL[f(home)] + sep + PL[f(away)]
        if year:
            uid += sep + str(year)
        return uid

    @staticmethod
    def _frac_to_dec(fraction, dp=_ODDS_DP):
        """ Convert a string representation of a fraction into a float. Expects
        fraction in the form 'n/d'.
        """
        try:
            fraction = str(fraction)
        except ValueError:
            print('Could not convert {} to string'.format(fraction))
            raise
        fraction = fraction.strip()
        for item in ['(', ')']:
            fraction = fraction.strip(item)
        n, d = fraction.split('/') # unpack numerator and denominator
        try: # check that they can be converted to integers
            n = int(n)
        except ValueError:
            print('Could not convert numerator ({}) to int'.format(n))
            raise
        try:
            d = int(d)
        except ValueError:
            print('Could not convert denominator ({}) to int'.format(d))
            raise
        return round(n/d, dp)

    @staticmethod
    def _text_to_date(date):
        """ Convert a string representation of a date into a Python date
        object. Assumes dates from the BBC.
        """
        try:
            day_name, day, month, year = date.split()
        except ValueError:
            print('Improperly formatted date ({})'.format(date))
            raise
        try:
            day = int(''.join([n for n in day if n.isdigit()]))
        except TypeError:
            print('Improperly formatted time ({})'.format(time))
            raise
        try:
            month = MONTHS.index(month.lower().strip())
        except ValueError:
            print('Non-existent month ({})'.format(month))
            raise
        try:
            year = int(year)
        except ValueError:
            print('Improper year ({})'.format(year))
            raise
        try:
            return datetime.date(year, month, day)
        except ValueError:
            print('Could not create date with day {0}, month {1} and year '
                  '{2}'.format(day, month, year))
            raise

    @staticmethod
    def _text_to_time(time):
        """ Convert a string representation of a time into a Python time
        object. Expects times from the BBC Fixtures webpage.
        """
        try:
            hour, minute = [int(i) for i in time.split(':')]
        except ValueError:
            print('Could not convert time ({}) to time object.'.format(time))
            raise
        try:
            return datetime.time(hour, minute, 0)
        except ValueError:
            print('Invalid time ({}:{})'.format(hour, minute))

    @staticmethod
    def _text_to_scores(score):
        """ Convert a string representation of a score into two integers.
        Expects score in the form '1-3'.
        """
        try:
            score = str(score)
        except ValueError:
            print('Could not convert {} to string'.format(string))
            raise
        score = score.strip()
        try:
            # expect that scores are split by '-'
            home, away = score.split('-')
        except ValueError:
            print('Home score ({}) not in correct format'.format(score))
            raise
        try: # check that scores can be converted to integers
            home = int(home)
        except ValueError:
            print('Could not convert home ({}) score to int'.format(home))
            raise
        try:
            away = int(away)
        except ValueError:
            print('Could not convert away ({}) score to int'.format(away))
            raise
        return (home, away)
