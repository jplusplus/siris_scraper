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
            data = [x for x in get_data_from_xml(content)]
            assert len(data) == 1740

    def test_get_data_from_xml_with_uttag_dimension(self):
        file_path = os.path.join(DATA_DIR, "exp_pers_amne_gr_skola_2014_sample.xml")
        with open(file_path) as f:
            content = f.read()
            data = [x for x in get_data_from_xml(content)]
            assert data[0]["uttag"] == "2015-08-17"

    def test_iter_options(self):
        select_elem = """
        <select name="psAr" onchange="reload(this.form);">\n
        <option selected="" value="2016">2016/17\n
        <option value="2015">2015/16\n
        <option value="2014">2014/15\n
        <option value="2013">2013/14\n
        <option value="2012">2012/13\n
        <option value="2011">2011/12\n
        <option value="2010">2010/11\n
        <option value="2009">2009/10\n
        <option value="2008">2008/09\n
        <option value="2007">2007/08\n
        <option value="2006">2006/07\n
        <option value="2005">2005/06\n
        <option value="2004">2004/05\n
        <option value="2003">2003/04\n
        <option value="2002">2002/03\n
        <option value="2001">2001/02\n
        <option value="2000">2000/01\n
        <option value="1999">1999/00\n
        <option value="1998">1998/99\n
        <option value="1997">1997/98\n
        </option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></select>
        """
        options = [x for x in iter_options(select_elem)]
        assert len(options) == 20

        select_elem = """
            <select name="psOmgang" onchange="reload(this.form);" title="Uttag ur l\xe4rarlegitimationsregistret">\n<option value="2">2015-08-17\n<option selected="" value="1">2015-02-04\n</option></option></select>
        """
        options = [x for x in iter_options(select_elem)]
        assert len(options) == 2

    def test_parse_value(self):
        assert parse_value(".") == (None, "missing or 0")
        assert parse_value("..") == (None, "too few")
        assert parse_value("5") == (5.0, None)
        assert parse_value("1 234") == (1234.0, None)

    def test_parse_period(self):
        assert parse_period(u"Valt år: 2016 Endast kommunal huvudman") == (u"2016", u"år")
        assert parse_period(u"Valt läsår: 2016/17 ") == (u"2016/17", u"läsår")
        assert parse_period(u"Vald termin: HT12") == (u"HT12", "termin")
