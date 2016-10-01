#!/usr/bin/env python3.5

""" store: functions for saving and retrieving from an SQL database.
"""

# built in modules
import os
import os.path
import sqlite3
import csv
import datetime

# package modules
from definitions import DB_SUB_DIR, DB_SUB_PATH, \
                        DB_BACKUP_SUB_PATH, ROW_HEADINGS

# CONSTANTS
FIELDS = ('INSERT INTO odds (id, uid, home, away, timestamp, date, time)'
          'VALUES (?, ?, ?, ?, ?, ?, ?)')
MAX_SAVES = 10 # for creating back-ups

# FUNCTIONS


def _connect():
    if not os.path.isdir(DB_SUB_DIR): # create folder for database
        os.mkdir(DB_SUB_DIR) # if it doesn't exist
    if os.path.exists(DB_SUB_PATH): # connection to the database, if it exists
        connection = sqlite3.connect(DB_SUB_PATH)
        try:
            c = connection.cursor()
        except sqlite3.Error as e:
            print('Could not open database. More details: {}'.format(e))
        return connection, c
    else:
        # otherwise create new database
        connection = sqlite3.connect(DB_SUB_PATH)
        c = connection.cursor()
        # and the main table
        c.execute(
            'CREATE TABLE odds (id INTEGER PRIMARY KEY, '
            'uid TEXT UNIQUE NOT NULL, home TEXT NOT NULL, '
            'away TEXT NOT NULL, timestamp TEXT, date TEXT, time TEXT, '
            'home_odds REAL, draw_odds REAl, away_odds REAL, '
            'home_score REAL, away_score REAL, result TEXT)')
        return connection, c


def _next_key(cursor):
    """ Return ID of last row entered.
    """
    cursor.execute('SELECT max(id) FROM odds')
    result = cursor.fetchone()[0]
    if result is None:
        return 0
    else:
        return result+1


def enter_fixtures(entries):
    connection, c = _connect() # initialise connection
    if not c:
        raise RuntimeError
    key = _next_key(c) # next available primary key
    existent = []
    for f in entries:
        data = (key,) + f.basic_info() + f.time_info()
        key += 1 # increment the key for the next entry
        try: # create new information, using instruction above
            c.execute(FIELDS, data)
        except sqlite3.IntegrityError:
            existent.append(f) # if a duplicate, keep track but continue
        except sqlite3.OperationalError as e:
            print('Operation failed - try again: {}'.format(e))
            raise # for other errors, abort and display error information
    if len(existent) and len(existent) <= 10: # print fixtures that already exist
        f = '\n'.join([e.uid for e in existent])
        print('The following already exist in the table:\n{}'.format(f))
        if len(existent) == 10:
            print('It appears that you have already captured data from'
                  ' this week.\n')
    elif len(existent) > 10:
        print('There were {} fixtures which could not be added to the '
              'database because they already exist.'.format(len(existent)))
    connection.commit() # close database
    connection.close()
    return connection, c


def update_odds(entries):
    """ Create entries in the database with the fixture information and the
    odds. If a fixture has no odds, add it to the database anyway.
    """
    connection, c = _connect() # initialise connection
    if not c:
        raise RuntimeError
    no_odds = []
    for f in entries:
        try: # get information from fixture
            timestamp = str(datetime.date.today())
            update = f.odds_info() + (timestamp, f.uid) 
        except AttributeError: # if there are no odds, continue but keep track
            no_odds.append(f)
        # try and update odds for the fixture
        try:
            c.execute('UPDATE odds SET home_odds = ?, draw_odds = ?, '
                      'away_odds = ?, timestamp = ? WHERE uid = ?', update)
        except sqlite3.OperationalError:
            if f not in no_odds:
                no_odds.append(f)
        except sqlite3.OperationalError as e:
            print('Operation failed - try again: {}'.format(e))
            raise # for other errors, abort and display error information
    if len(no_odds) and len(no_odds) <= 10: # print fixture without odds
        f = '\n'.join([e.uid for e in no_odds])
        print('No odds were present for the following:\n{}'.format(f))
        print('These fixtures were still added to the database.\n')
    elif len(no_odds) > 10:
        print('There were {} fixtures without odds. These fixtures were '
              'processed anyway.'.format(len(no_odds)))
    connection.commit() # close database
    connection.close()
    return connection, c


def update_results(entries):
    """ For any fixture that exists in the database, update the results from
    a container. If the a fixture in the container does not match a result in
    the database, no change is made.
    """
    connection, c = _connect() # initialise connection to database
    if not c:
        raise RuntimeError
    errors, db_error = [], [] # lists to hold cases where errors occur
    for f in entries:
        try: # get information from fixture
            data = f.result_info() + (f.uid,)
        except AttributeError: # keep track of problems in retrieving results
            errors.append(f)
            continue # don't update the database where results were found
        try: # update database with result
            c.execute('UPDATE odds SET home_score = ?, away_score = ?, '
                      'result = ? WHERE uid = ?', data)
        except (sqlite3.IntegrityError, sqlite3.OperationalError):
            db_error.append(f) # keep track of database problems
    if len(errors): # print fixtures without scores
        f = '\n'.join([e.uid for e in errors])
        print('No scores were present for the following:\n{}'.format(f))
        print('These fixtures were not added to the database.\n')
    if len(db_error): # print other errors
        f = '\n'.join([e.uid for e in errors])
        print('The following could not be added to the database:\n{}'.format(f)
              )
        print('These fixtures were not added to the database.\n')
    connection.commit() # close database
    connection.close()
    return connection, c


def export(path, overwrite=False):
    """ Download entire database and save as CSV at the specified location.
    """
    if not overwrite and os.path.isfile(path): # open file if it exists
        raise FileExistsError('File already exists: {}'.format(path))
    else: # otherwise create a file
        try:
            f = open(path, 'w')
        except Exception as e:
            print('Could not create CSV file. More details: {}'.format(e))
    connection, c = _connect()
    if not c:
        raise RuntimeError
    data = c.execute('SELECT * FROM odds').fetchall() # download all records
    n = sum([len(row) for row in data]) # get number or records
    writer = csv.writer(f)
    writer.writerow(ROW_HEADINGS)
    for line in data: # write data to csv file
        writer.writerow(line)
    f.close()
    return n


def backup():
    """ Create a dated copy of the database.
    """
    today = str(datetime.date.today())
    # file path with date
    trial_path = DB_BACKUP_SUB_PATH + 'odds-{}.sqlite'
    addition = today
    path = trial_path.format(addition) # path containing the date
    c = 0 # counter for modifying file name
    while os.path.isfile(path):
        c += 1 # increment file name
        addition = today + '-' + str(c) # new addition to path
        path = trial_path.format(addition) # path with date and number
        if c >= MAX_SAVES:
            raise RuntimeError('too many backup attempts')
    dest = open(path, 'wb')
    source = open(DB_SUB_PATH, 'rb')
    dest.write(source.read())
    source.close()
    dest.close()
    return path
