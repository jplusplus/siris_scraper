# encoding: utf-8
"""Test utility functions."""
from unittest import TestCase
import os

from siris.utils import get_data_from_xml, iter_options, parse_value, parse_period
from requests.exceptions import HTTPError

DATA_DIR = "tests/data"

class TestUtils(TestCase):

    def setUp(self):
        pass

    def get_data_from_xml(self):
        file_path = os.path.join(DATA_DIR, "exp_kostnader_kommun_fklass_2016.xml")
        with open(file_path) as f:
            content = f.read()
            data = [x for x in parse_xml_dataset(content)]
            assert len(data) == 1740

    def test_iter_options(self):
        #TBD
        pass

    def test_parse_value(self):
        assert parse_value(".") == (None, "missing or 0")
        assert parse_value("..") == (None, "too few")
        assert parse_value("5") == (5.0, None)
        assert parse_value("1 234") == (1234.0, None)

    def test_parse_period(self):
        assert parse_period(u"Valt år: 2016 Endast kommunal huvudman") == (u"2016", u"år")
        assert parse_period(u"Valt läsår: 2016/17 ") == (u"2016/17", u"läsår")
        assert parse_period(u"Vald termin: HT12") == (u"HT12", "termin")
