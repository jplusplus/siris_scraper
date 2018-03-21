# encoding: utf-8
"""Tests for browsing the api."""
from unittest import TestCase

from siris.scraper import SirisScraper, Verksamhetsform
from requests.exceptions import HTTPError


class TestSirisScraper(TestCase):

    def setUp(self):
        self.scraper = SirisScraper()

    def test_verksamhetsformer(self):
        # This test depends on the content of the site
        collections = self.scraper.items
        assert len(collections) == 16
        for collection in collections:
            assert isinstance(collection, Verksamhetsform)

        verksamhet = collections.get_by_label(u"Förskoleklass")
        assert isinstance(collection, Verksamhetsform)


    def test_get_datasets(self):
        # This test depends on the content of the site
        collections = self.scraper.items
        verksamhet = collections.get_by_label(u"Förskoleklass")
        datasets = verksamhet.items
        assert len(datasets) == 5

    def test_periods_property(self):
        collections = self.scraper.items
        verksamhet = collections.get_by_label(u"Förskoleklass")
        dataset = verksamhet.items[0]
        assert isinstance(dataset.periods, list)
        assert len(dataset.periods) > 0

        verksamhet = collections.get_by_label(u"Grundskolan")
        dataset = verksamhet.items["101"]
        assert isinstance(dataset.periods, list)
        assert len(dataset.periods) > 0

    def test_uttag(self):
        collections = self.scraper.items
        verksamhet = collections.get_by_label(u"Grundskolan")
        dataset = verksamhet.items["99"]
        uttag = dataset.get_uttag("2014")
        assert len(uttag) == 2

        assert dataset.get_latest_uttag("2014") == ("2", "2015-08-17")
