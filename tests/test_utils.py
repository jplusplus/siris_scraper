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
            assert data[0]["niva"] == "skola"

    def test_get_data_from_xml_with_uttag_dimension(self):
        file_path = os.path.join(DATA_DIR, "exp_pers_amne_gr_skola_2014_sample.xml")
        with open(file_path) as f:
            content = f.read()
            data = [x for x in get_data_from_xml(content)]
            assert data[0]["uttag"] == "2015-08-17"

    def test_get_data_from_xml_with_amne_dimension(self):
        file_path = os.path.join(DATA_DIR, "exp_personal_alder_gr_kommun_2017_sample.xml")
        with open(file_path) as f:
            content = f.read()
            data = [x for x in get_data_from_xml(content)]
            assert "amne" in data[0]
            assert data[0]["amne"] == u"Samtliga lärare"

    def test_get_data_at_different_levels(self):
        file_path = os.path.join(DATA_DIR, "exp_pers_amne_gy_kommun_amne_2018.xml")
        with open(file_path) as f:
            content = f.read()
            data = [x for x in get_data_from_xml(content)]
            assert data[0]["niva"] == "kommun"

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

    def test_iter_options_complex(self):
        select_elem = '<select name="pnExport" onchange="reload(this.form);">\n<option value="23">Antal elever per \xc3\xa5rskurs\n<option value="6">Antal elever per \xc3\xa5rskurs\n<option value="146">Antal elever per \xc3\xa5rskurs\n<option value="53">Beh\xc3\xb6righet till gymnasieskolan, fr.o.m. 2011\n<option value="155">Beh\xc3\xb6righet till gymnasieskolan, fr.o.m. 2011\n<option value="5">Beh\xc3\xb6righet till gymnasieskolan, fr.o.m. 2011\n<option value="30">Beh\xc3\xb6righet till gymnasieskolan, t.o.m. 2010\n<option value="8">Beh\xc3\xb6righet till gymnasieskolan, t.o.m. 2010\n<option value="202">Beslutade anm\xc3\xa4lningar\n<option value="204">Beslutade anm\xc3\xa4lningar\n<option value="71">Betyg per \xc3\xa4mne \xc3\xa5rskurs 6\n<option value="72">Betyg per \xc3\xa4mne \xc3\xa5rskurs 6\n<option value="173">Betyg per \xc3\xa4mne \xc3\xa5rskurs 6\n<option value="145">Betyg \xc3\xa5rskurs 6, andel som uppn\xc3\xa5tt kunskapskraven (A-E), med/utan nyinvandrade och ok\xc3\xa4nd bakgrund\n<option value="142">Betyg \xc3\xa5rskurs 6, andel som uppn\xc3\xa5tt kunskapskraven (A-E), med/utan nyinvandrade och ok\xc3\xa4nd bakgrund\n<option value="175">Betyg \xc3\xa5rskurs 6, andel som uppn\xc3\xa5tt kunskapskraven (A-E), med/utan nyinvandrade och ok\xc3\xa4nd bakgrund\n<option value="176">Betyg \xc3\xa5rskurs 6, andel som uppn\xc3\xa5tt kunskapskraven (A-E), per k\xc3\xb6n\n<option value="144">Betyg \xc3\xa5rskurs 6, andel som uppn\xc3\xa5tt kunskapskraven (A-E), per k\xc3\xb6n\n<option value="94">Betyg \xc3\xa5rskurs 6, andel som uppn\xc3\xa5tt kunskapskraven (A-E), per k\xc3\xb6n\n<option value="143">Betyg \xc3\xa5rskurs 6, andel som uppn\xc3\xa5tt kunskapskraven (A-E), samtliga elever\n<option value="87">Betyg \xc3\xa5rskurs 6, andel som uppn\xc3\xa5tt kunskapskraven (A-E), samtliga elever\n<option value="174">Betyg \xc3\xa5rskurs 6, andel som uppn\xc3\xa5tt kunskapskraven (A-E), samtliga elever\n<option value="203">Inkomna anm\xc3\xa4lningar\n<option value="201">Inkomna anm\xc3\xa4lningar\n<option value="32">Kostnader per kommun\n<option value="235">Kostnader per l\xc3\xa4n\n<option value="60">Pendling mellan hem- och skolkommun per typ av huvudman\n<option value="265">Personalstatistik\n<option value="81">Personalstatistik\n<option value="154">Personalstatistik\n<option value="16">Personalstatistik\n<option value="101">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet i minst ett \xc3\xa4mne\n<option value="177">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet i minst ett \xc3\xa4mne\n<option value="99">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet i minst ett \xc3\xa4mne\n<option value="254">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet i minst ett \xc3\xa4mne\n<option value="281">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet i minst ett \xc3\xa4mne, j\xc3\xa4mf\xc3\xb6rt med f\xc3\xb6reg\xc3\xa5ende \xc3\xa5r, antal heltidstj\xc3\xa4nster\n<option value="278">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet i minst ett \xc3\xa4mne, j\xc3\xa4mf\xc3\xb6rt med f\xc3\xb6reg\xc3\xa5ende \xc3\xa5r, antal heltidstj\xc3\xa4nster\n<option value="280">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet i minst ett \xc3\xa4mne, j\xc3\xa4mf\xc3\xb6rt med f\xc3\xb6reg\xc3\xa5ende \xc3\xa5r, antal l\xc3\xa4rare\n<option value="276">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet i minst ett \xc3\xa4mne, j\xc3\xa4mf\xc3\xb6rt med f\xc3\xb6reg\xc3\xa5ende \xc3\xa5r, antal l\xc3\xa4rare\n<option value="285">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet i minst ett \xc3\xa4mne, \xc3\xa5k 1-3\n<option value="163">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet i minst ett \xc3\xa4mne, \xc3\xa5k 1-3\n<option value="164">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet i minst ett \xc3\xa4mne, \xc3\xa5k 4-6\n<option value="286">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet i minst ett \xc3\xa4mne, \xc3\xa5k 4-6\n<option value="284">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet i minst ett \xc3\xa4mne, \xc3\xa5k 7-9\n<option value="111">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet i minst ett \xc3\xa4mne, \xc3\xa5k 7-9\n<option value="102">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet per \xc3\xa4mne\n<option value="100">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet per \xc3\xa4mne\n<option value="267">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet per \xc3\xa4mne\n<option value="179">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet per \xc3\xa4mne\n<option value="161">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet per \xc3\xa4mne, \xc3\xa5k 1-3\n<option value="183">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet per \xc3\xa4mne, \xc3\xa5k 1-3\n<option value="182">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet per \xc3\xa4mne, \xc3\xa5k 4-6\n<option value="162">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet per \xc3\xa4mne, \xc3\xa5k 4-6\n<option value="112">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet per \xc3\xa4mne, \xc3\xa5k 7-9\n<option value="181">Personalstatistik med l\xc3\xa4rarlegitimation och beh\xc3\xb6righet per \xc3\xa4mne, \xc3\xa5k 7-9\n<option value="168">Personalstatistik, \xc3\xa5ldersf\xc3\xb6rdelning\n<option value="274">Personalstatistik, \xc3\xa5ldersf\xc3\xb6rdelning med leg.\n<option value="171">Relationen mellan nationella prov och slutbetyg \xc3\xa5rskurs 9, per huvudman, svenska/svenska som andraspr\xc3\xa5k, matematik och engelska\n<option value="11">Relationen mellan nationella prov och slutbetyg \xc3\xa5rskurs 9, per kommun, svenska/svenska som andraspr\xc3\xa5k, matematik och engelska\n<option value="2">Relationen mellan nationella prov och slutbetyg \xc3\xa5rskurs 9, per k\xc3\xb6n, svenska/svenska som andraspr\xc3\xa5k, matematik och engelska\n<option value="273">Relationen mellan nationella prov och slutbetyg \xc3\xa5rskurs 9, per l\xc3\xa4n, svenska/svenska som andraspr\xc3\xa5k, matematik och engelska\n<option value="1">Relationen mellan nationella prov och slutbetyg \xc3\xa5rskurs 9, svenska/svenska som andraspr\xc3\xa5k, matematik och engelska\n<option value="4">Relationen mellan nationella prov och slutbetyg \xc3\xa5rskurs 9, totalt och per k\xc3\xb6n, biologi, fysik och kemi\n<option value="123">Relationen mellan nationella prov och slutbetyg \xc3\xa5rskurs 9, totalt och per k\xc3\xb6n, geografi, historia, religionskunskap och samh\xc3\xa4llskunskap\n<option value="84">Relationen mellan nationella prov och terminsbetyg \xc3\xa5rskurs 6\n<option value="192">Relationen mellan nationella prov och terminsbetyg \xc3\xa5rskurs 6\n<option value="83">Relationen mellan nationella prov och terminsbetyg \xc3\xa5rskurs 6\n<option value="12">Resultat nationella prov \xc3\xa5rskurs 3\n<option value="52">Resultat nationella prov \xc3\xa5rskurs 3\n<option value="191">Resultat nationella prov \xc3\xa5rskurs 3\n<option value="190">Resultat nationella prov \xc3\xa5rskurs 6\n<option value="51">Resultat nationella prov \xc3\xa5rskurs 6\n<option value="49">Resultat nationella prov \xc3\xa5rskurs 6\n<option value="194">Resultat nationella prov \xc3\xa5rskurs 9, per delprov och k\xc3\xb6n - Engelska, Matematik och Svenska/svenska som andraspr\xc3\xa5k\n<option value="193">Resultat nationella prov \xc3\xa5rskurs 9, per delprov och k\xc3\xb6n - Engelska, Matematik och Svenska/svenska som andraspr\xc3\xa5k\n<option value="195">Resultat nationella prov \xc3\xa5rskurs 9, per delprov och k\xc3\xb6n - Engelska, Matematik och Svenska/svenska som andraspr\xc3\xa5k\n<option value="199">Resultat nationella prov \xc3\xa5rskurs 9, provbetyg per k\xc3\xb6n - Biologi, Fysik och Kemi\n<option value="196">Resultat nationella prov \xc3\xa5rskurs 9, provbetyg per k\xc3\xb6n - Engelska, Matematik och Svenska/svenska som andraspr\xc3\xa5k\n<option value="198">Resultat nationella prov \xc3\xa5rskurs 9, provbetyg per k\xc3\xb6n - Engelska, Matematik och Svenska/svenska som andraspr\xc3\xa5k\n<option value="197">Resultat nationella prov \xc3\xa5rskurs 9, provbetyg per k\xc3\xb6n - Engelska, Matematik och Svenska/svenska som andraspr\xc3\xa5k\n<option value="200">Resultat nationella prov \xc3\xa5rskurs 9, provbetyg per k\xc3\xb6n - Geografi, Historia, Religionskunskap, Samh\xc3\xa4llskunskap\n<option value="95">Salsa, skolenheters resultat av slutbetygen i \xc3\xa5rskurs 9 med h\xc3\xa4nsyn till elevsammans\xc3\xa4ttningen\n<option value="148">Slutbetyg per \xc3\xa4mne \xc3\xa5rskurs 9, fr.o.m. 2013\n<option value="92">Slutbetyg per \xc3\xa4mne \xc3\xa5rskurs 9, fr.o.m. 2013\n<option value="93">Slutbetyg per \xc3\xa4mne \xc3\xa5rskurs 9, fr.o.m. 2013\n<option value="138">Slutbetyg \xc3\xa5rskurs 9, samtliga elever\n<option value="150">Slutbetyg \xc3\xa5rskurs 9, samtliga elever\n<option value="139">Slutbetyg \xc3\xa5rskurs 9, samtliga elever\n<option value="26">Slutbetyg \xc3\xa5rskurs 9, uppdelat per f\xc3\xb6r\xc3\xa4ldrarnas h\xc3\xb6gsta utbildningsniv\xc3\xa5\n<option value="29">Slutbetyg \xc3\xa5rskurs 9, uppdelat per f\xc3\xb6r\xc3\xa4ldrarnas h\xc3\xb6gsta utbildningsniv\xc3\xa5\n<option value="140">Slutbetyg \xc3\xa5rskurs 9, uppdelat per k\xc3\xb6n\n<option value="141">Slutbetyg \xc3\xa5rskurs 9, uppdelat per k\xc3\xb6n\n<option value="109">Slutbetyg \xc3\xa5rskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade\n<option value="110">Slutbetyg \xc3\xa5rskurs 9, uppdelat per nyinvandrade och exklusive nyinvandrade\n<option value="25">Slutbetyg \xc3\xa5rskurs 9, uppdelat per svensk och utl\xc3\xa4ndsk bakgrund\n<option value="28">Slutbetyg \xc3\xa5rskurs 9, uppdelat per svensk och utl\xc3\xa4ndsk bakgrund\n</option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></option></select>'

        options = [x for x in iter_options(select_elem)]
        assert len(options) == 96


    def test_parse_value(self):
        assert parse_value(".") == (None, "missing or 0")
        assert parse_value("..") == (None, "too few")
        assert parse_value("5") == (5.0, None)
        assert parse_value("1 234") == (1234.0, None)

    def test_parse_period(self):
        assert parse_period(u"Valt år: 2016 Endast kommunal huvudman") == (u"2016", u"år")
        assert parse_period(u"Valt läsår: 2016/17 ") == (u"2016/17", u"läsår")
        assert parse_period(u"Vald termin: HT12") == (u"HT12", "termin")
