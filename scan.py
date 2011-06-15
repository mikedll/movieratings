#!/usr/bin/python

import mechanize
from pyquery import PyQuery as pq
import sys
import cPickle
import os
import re

class Database:
    def __init__(self, path = None):
        self.protocol = 2
        if path is None:
            path = os.path.dirname(__file__)
        self.path = path
        self.scores = {}
        self._load()


    def add(self, movie, score):
        self.scores[movie] = score

    def _load(self):
        if not os.path.exists(self._picklepath()):
            self.scores = {}
            return
        fileio = file(self._picklepath(), "rb")
        unpickler = cPickle.Unpickler(fileio)
        self.scores = unpickler.load()
        fileio.close()

    def _picklepath(self):
        return os.path.join( self.path, 'scores.pkl')

    def flush(self):
        fileio = file(self._picklepath(), "wb")
        pickler = cPickle.Pickler(fileio, protocol=self.protocol)
        pickler.dump(self.scores)
        fileio.close()


def movies_list():
    root = "http://www.metacritic.com"
    path = '/browse/movies/release-date/theaters/date'
    all_releases_by_metascore = '/browse/dvds/release-date/available/metascore?view=condensed'

    req_path = root + all_releases_by_metascore

    browser = mechanize.Browser()
    response = browser.open(req_path)
    if response is None:
        print "Unable to open path %s" % req_path
        return None

    html = response.read()
    cache = file("response.html", "w")
    cache.write(html)
    cache.close()

    return pq(html)


def harvest():
    db = Database()
    movies = movies_list()
    for movie in movies('li.product'):
        movieq = pq(movie)
        movie = movieq('.product_title').text()
        scorestring = movieq('.score_wrap span.metascore').text()
        if scorestring is None:
            print "Unable to decipher score for movie '%s'" % movie
            continue

        matches = re.match( '^\w*(\d+)\w*$', scorestring )

        if matches is None:
            print "Unable to find score for %s" % movie
            continue

        score = int( matches.group(0) )
        
        db.add(movie, score)
        print "Discovered %s: %s" % (movie, score)

    db.flush()

def persisted():
    db = Database()
    for movie in db.scores.keys():
        print "%s: %s" % (movie, db.scores[movie])

if __name__ == '__main__':
    # harvest()
    persisted()

