#!/usr/bin/env python3.5

""" tests: unit tests for the odds module.
"""

# built-in modules
import datetime

# package modules
import fixture
import retrieve
import store
import definitions


def test_fixture():
    """ Test the Fixture class.
    """
    print('Testing Fixture class')
    f = fixture.Fixture('Arsenal', 'Tottenham')
    f.set_odds('1/10', '100/1', '5000/1')
    f.set_result('8-0')
    dp = fixture.ODDS_DP
    dec = lambda frac: round(frac, dp)
    try:
        assert f.basic_info() == ('ARSENAL-TOTTENHAM', 'Arsenal', 'Tottenham')
    except AssertionError:
        print(f.basic_info(), ('ARSENAL-TOTTENHAM', 'Arsenal', 'Tottenham'))
        raise
    try:
        assert f.odds_info() == (dec(1/10), dec(100/1), dec(5000/1))
    except AssertionError:
        print(f.odds_info(), (dec(1/10), dec(100/1), dec(5000/1)))
        raise
    try:
        assert f.result_info() == (8, 0, 'H')
    except AssertionError:
        print(f.result_info(), (8, 0, 'H'))
        raise
    return


def test_retrieve_odds():
    print('Testing odds retrieval')
    r = retrieve.get_odds()
    try:
        assert all([type(f) == fixture.Fixture for f in r])
        assert r != []
    except AssertionError:
        print('Not created any fixtures: {}'.format(r))
        raise
    try:
        assert len(r) >= int(len(definitions.PL)/2)
    except AssertionError:
        print('Not enough fixtures: {0}\n{1}'.format(len(r), r))
        raise
    return


def test_retrieve_results():
    print('Testing results retrieval')
    r = retrieve.get_results()
    try:
        assert all([type(f) == fixture.Fixture for f in r])
        assert r != []
    except AssertionError:
        print('Not created any fixtures: {}'.format(r))
        raise
    try:
        assert len(r) >= int(len(definitions.PL)/2)
    except AssertionError:
        print('Not enough fixtures: {0}\n{1}'.format(len(r), r))
        raise
    return


def test_connection():
    print('Testing connection to database')
    connection, c = store._connect()
    try:
        assert c
    except AssertionError:
        print('Cannot open database')
        raise

if __name__ == '__main__':
    test_fixture()
    test_retrieve_odds()
    test_retrieve_results()
    test_connection()
    print('Tests completed')
