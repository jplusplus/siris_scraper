# encoding: utf-8
import requests
from bs4 import BeautifulSoup
import re
from statscraper import (BaseScraper, Collection, DimensionValue,
                         Dataset, Dimension, Result)
from siris.utils import get_data_from_xml, parse_period, parse_value, iter_options
from copy import deepcopy

BASE_URL = u"http://siris.skolverket.se"


class SirisScraper(BaseScraper):

    def _fetch_itemslist(self, current_item):
        enrty_url = BASE_URL + "/siris/ris.export_stat.form"
        # Get start page
        if current_item.is_root:
            html = self._get_html(enrty_url)
            soup = BeautifulSoup(html, 'html.parser')
            select_elem = soup.select_one("select[name='psVerksamhetsform']")
            # <option selected="" value="15">Fritidshem'
            for value, label in iter_options(select_elem):
                yield Verksamhetsform(value, label.decode("utf-8"))

        elif isinstance(current_item, Verksamhetsform):
            url = "{}?psVerksamhetsform={}".format(enrty_url, current_item.id)
            html = self._get_html(url)
            soup = BeautifulSoup(html, 'html.parser')
            select_elem = soup.select_one("select[name='pnExport']")
            for value, label in iter_options(select_elem):
                yield SirisDataset(value, label.decode("utf-8"), blob=html)


        # Get links to datasets


    def _fetch_allowed_values(self, dimension):
        """Allowed values are only implemented for regions.
        Ie units would need to be fetched trough an json api.
        """
        pass

    def _fetch_dimensions(self, dataset):
        yield Dimension("kommunkod")
        yield Dimension("kommun_namn")
        yield Dimension("huvudman")
        yield Dimension("huvudman_name")
        yield Dimension("skolnamn")
        yield Dimension("skol_kod")
        yield Dimension("amne")
        yield Dimension("period")
        yield Dimension("periodicity")
        yield Dimension("uttag")
        yield Dimension("variable")
        yield Dimension("status")


    def _fetch_data(self, dataset, query):
        """Make the actual query.

        The only queryable dimensions are period.

        >>> dataset.fetch({"period": "2016"})
        >>> dataset.fetch({"period": ["2015", "2016"]})
        >>> dataset.fetch({"period": "*"}) # Get all periods
        """
        default_query = {
            "period": dataset.latest_period[1],
        }
        if query is None:
            query = {}

        default_query.update(query)
        query = default_query
        allowed_query_dims = ["period"]

        for dim in query.keys():
            if dim not in allowed_query_dims:
                msg = "Querying on {} is not implemented yet".format(dim)
                raise NotImplementedError(msg)

        if query["period"] == "*":
            periods = [x[1] for x in dataset.periods]
        else:
            if not isinstance(query["period"], list):
                periods = [query["period"]]
            else:
                periods = query["period"]

        # Get the period id's needed to build url
        periods = [dataset._get_period_id(x) for x in periods]

        for period in periods:
            # Hack: For datasets with multiple uttag we get the latest
            # This should rather be a part of query
            if dataset.has_uttag:
                uttag = dataset.get_latest_uttag(period)[0]
            else:
                uttag = None
            url = dataset.get_xml_url(period, uttag)
            xml_data = self._get_html(url)
            for datapoint in get_data_from_xml(xml_data):
                value = datapoint["value"]
                del datapoint["value"]
                yield Result(value, datapoint)


    ###
    # HELPER METHODS
    ###
    def _get_html(self, url):
        """ Get html from url
        """
        self.log.info(u"/GET {}".format(url))
        r = requests.get(url)
        if hasattr(r, 'from_cache'):
            if r.from_cache:
                self.log.info("(from cache)")

        r.raise_for_status()

        return r.content

    def _post_html(self, url, payload):
        self.log.info(u"/POST {} with {}".format(url, payload))
        r = requests.post(url, payload)
        r.raise_for_status()

        return r.content

    def _get_json(self, url):
        """ Get json from url
        """
        self.log.info(u"/GET " + url)
        r = requests.get(url)
        if hasattr(r, 'from_cache'):
            if r.from_cache:
                self.log.info("(from cache)")
        r.raise_for_status()

        return r.json()


    @property
    def log(self):
        if not hasattr(self, "_logger"):
            self._logger = PrintLogger()
        return self._logger



class SirisDataset(Dataset):

    @property
    def url(self):
        """Get base url of dataset.
        """
        if not hasattr(self, "_url"):
            url = "{}/siris/ris.export_stat.form?psVerksamhetsform={}&pnExport={}"\
                  .format(BASE_URL, self.parent.id, self.id)
            # To get the full url with all necessary url params we first have
            # ot make one query and parse all hidden inputs before we can
            # construct the actual url
            html = self.scraper._get_html(url)
            soup = BeautifulSoup(html, 'html.parser')
            for elem in soup.select("input[type='hidden']"):
                url += "&{}={}".format(elem["name"], elem["value"])
            self._url = url

        return self._url

    def get_url(self, period=None, uttag=1):
        """Get the url for a spefic period and uttag.

        TODO: Make this work with uttag labels as well (dates)

        :param period: a period id (ie "2015")
        :param uttag: an uttag id (typically 1|2)
        """
        url = deepcopy(self.url)

        if period is not None:
            url += "&psAr={}".format(period)
        if uttag is not None:
            url += "&psOmgang={}".format(uttag)

        return url

    def get_xml_url(self, period, uttag=1):
        """Get download link."""
        url = self.get_url(period=period, uttag=uttag)
        html = self.scraper._get_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        xml_url = BASE_URL + soup.select_one("a[href*=XML]")["href"]
        xml_url = re.sub("psVerksamhetsar=\d\d\d\d",
                     "psVerksamhetsar={}".format(period),
                     xml_url)
        return xml_url

    @property
    def periods(self):
        """Get all available periods (years, semesters)."""
        select_elem = self.soup.select_one("select[name='psAr']")
        return [(x[0], x[1]) for x in iter_options(select_elem)]


    @property
    def latest_period(self):
        """Get the latest timepoint available in dataset."""
        return self.periods[0]

    @property
    def has_uttag(self):
        """Some dataset (like lärarebehörighet) my be published multiple
        times per year (="uttag"). This property checks if this is such a
        dataset.
        """
        return bool(self.soup.select_one("select[name='psOmgang']"))

    def get_uttag(self, period):
        """Get all available 'uttag' in a given period (year).
        Uttag are relevant to "lärarbehörighet" that some years (ie 2014/15)
        have been published multiple times

        :param period: a period id
        :returns: id and label of all uttag (if any) as tuples
        """
        url = self.get_url(period)
        html = self.scraper._get_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        select_elem = soup.select_one("select[name='psOmgang']")
        return [(x[0], x[1]) for x in iter_options(select_elem)]

    def get_latest_uttag(self, period):
        """Get the uttag that appaear first in list. Uttag differ from year to year.

        :returns: id and label of latest uttag (if any) as tuple
        """
        uttag = [x for x in self.get_uttag(period)]
        if len(uttag) > 0:
            return uttag[0]
        else:
            return None


    def _get_period_id(self, period_label):
        if not hasattr(self, "_period_translattion"):
            self._period_translattion = dict([(x[1], x[0]) for x in self.periods])
        return self._period_translattion[period_label]



    @property
    def html(self):
        if not hasattr(self, "_html"):
            self._html = self.scraper._get_html(self.url)
        return self._html


    @property
    def soup(self):
        if not hasattr(self, "_soup"):
            self._soup = BeautifulSoup(self.html, 'html.parser')
        return self._soup


class Verksamhetsform(Collection):
    collection_type = "verksamhetsform"



class SirisDimension(Dimension):
    """docstring for VantetiderDimension"""
    pass




class PrintLogger():
    """ Empyt "fake" logger
    """

    def log(self, msg, *args, **kwargs):
        print msg

    def debug(self, msg, *args, **kwargs):
        print msg

    def info(self, msg, *args, **kwargs):
        print msg

    def warning(self, msg, *args, **kwargs):
        print msg

    def error(self, msg, *args, **kwargs):
        print msg

    def critical(self, msg, *args, **kwargs):
        print msg
