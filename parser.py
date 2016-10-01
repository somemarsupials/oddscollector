#!/usr/bin/env python3.5

""" parser: a class for parsing the BBC Sports website.
"""

# built in modules
from html.parser import HTMLParser 

# CLASSES


class BBCParser(HTMLParser):

    def __init__(self):
        super(BBCParser, self).__init__()
        self.current_date = None
        self.in_table = False
        self.in_date = False
        self.in_ko = False
        self.in_score = [False, False]
        self.in_home = [False, False]
        self.in_away = [False, False]
        self.div_count = 0
        self.home = []
        self.away = []
        self.dates = []
        self.ko = []
        self.scores = []

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and ('class', 'stats-body') in attrs:
            self.in_table = True
        elif tag == 'div':
            self.div_count += 1
        elif tag == 'h2' and ('class', 'table-header') in attrs:
            self.in_date = True
        elif tag == 'span' and ('class', 'team-home teams') in attrs:
            self.in_home[0] = True
        elif tag == 'a' and self.in_home[0]:
            self.in_home[1] = True
        elif tag == 'span' and ('class', 'team-away teams') in attrs:
            self.in_away[0] = True
        elif tag == 'a' and self.in_away[0]:
            self.in_away[1] = True
        elif tag == 'td' and self.in_table and ('class', 'kickoff') in attrs:
            self.in_ko = True
        elif tag == 'span' and ('class', 'score') in attrs:
            self.in_score[0] = True
        elif tag == 'abbr':
            self.in_score[1] = True

    def handle_endtag(self, tag):
        if tag == 'div' and self.div_count == 0:
            self.in_table = False
        elif tag == 'div':
            self.div_count -= 1
        elif tag == 'h2':
            self.in_date = False
        elif tag == 'span' and any(self.in_home):
            self.in_home = [False, False]
        elif tag == 'span' and any(self.in_away):
            self.in_away = [False, False]
        elif tag == 'td' and self.in_ko:
            self.in_ko = False
        elif tag == 'abbr' and any(self.in_score):
            self.in_score = [False, False]

    def handle_data(self, data):
        data = data.strip().strip('\n').strip()
        if self.in_table:
            if self.in_date:
                self.current_date = data
                self.in_date = False
            if all(self.in_home):
                self.home.append(data)
                self.in_home = [False, False]
                self.dates.append(self.current_date)
            if all(self.in_away):
                self.away.append(data)
                self.in_away = [False, False]
            if self.in_ko:
                self.ko.append(data)
            if all(self.in_score):
                self.scores.append(data)
                self.in_score = [False, False]

    def run_checks(self):
        attrs = [self.dates, self.ko, self.scores]
        if len(self.home) != len(self.away):
            raise ValueError('Mismatch with home ({0}) and away ({1}) '
                             'teams'.format(len(self.home), len(self.away)))
        if len(self.dates) != len(self.home) and self.dates:
                raise ValueError('Too few dates ({})'.format(len(self.dates)))
        if len(self.ko) != len(self.home) and self.ko:
                raise ValueError('Too few times ({})'.format(len(self.ko)))
        if len(self.scores) != len(self.home) and self.scores:
                raise ValueError('Too few scores ({})'.format(len(scores)))
        
            
