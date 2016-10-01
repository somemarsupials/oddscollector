#!/usr/bin/env python3.5

""" odds: a package for downloading and saving football fixtures, odds and
results. Designed to retrieve data from the BBC and Oddschecker.
"""

import retrieve
import store

def update():
    f = retrieve.get_fixtures()
    try:
        odds = retrieve.get_odds(fixtures=f)
    except IndexError as e:
        print('Could not get odds. Error: {}'.format(e))
    try:
        store.enter_fixtures(f)
    except Exception as e:
        print('Could not create fixtures. Error: {}'.format(e))
    try:
        store.update_odds(odds)
    except Exception as e:
        print('Could not update database with odds. Error: {}'.format(e))
    try:
        results = retrieve.get_results()
    except ValueError as e:
        print('Could not get scores. Error: {}'.format(e))
    try:
        store.update_results(results)
    except Exception as e:
        print('Could not update database with scores. Error: {}'.format(e))

if __name__ == '__main__':
    update()
