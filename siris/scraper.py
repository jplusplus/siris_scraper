# encoding: utf-8
import requests
from bs4 import BeautifulSoup

from statscraper import (BaseScraper, Collection, DimensionValue,
                         Dataset, Dimension, Result)
from siris.utils import get_data_from_xml, parse_period, parse_value, iter_options

BASE_URL = u"http://siris.skolverket.se/siris/"


class SirisScraper(BaseScraper):

    def _fetch_itemslist(self, current_item):
        enrty_url = BASE_URL + "ris.export_stat.form"
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
        yield Dimension("unit")
        yield Dimension("kommunkod")
        yield Dimension("kommun_namn")
        yield Dimension("huvudman")
        yield Dimension("period")
        yield Dimension("periodicity")
        yield Dimension("variable")
        yield Dimension("status")


    def _fetch_data(self, dataset, query):
        """Make the actual query.

        The only queryable dimension is period.

        >>> dataset.fetch({"period": "2016"})
        >>> dataset.fetch({"period": ["2015", "2016"]})
        >>> dataset.fetch({"period": "*"}) # Get all periods
        """
        if query is None:
            query = {}
        allowed_query_dims = ["period"]

        for dim in query.keys():
            if dim not in allowed_query_dims:
                msg = "Querying on {} is not implemented yet".format(dim)
                raise NotImplemented(msg)
        if query is None or "period" not in query:
            periods = [dataset.latest_period[1]]
        elif query["period"] == "*":
            periods = [x[1] for x in dataset.periods]
        else:
            if not isinstance(query["period"], list):
                periods = [query["period"]]
            else:
                periods = query["period"]

        # Get the period id's needed to build url
        periods = [dataset._get_period_id(x) for x in periods]

        query_url = BASE_URL + "ris.export_stat.export"
        for period in periods:
            url = "{query_url}?pnExportID={dataset_id}&psVerksamhetsar={period}&psFormat=XML".format(
                query_url=query_url,
                dataset_id=dataset.id,
                period=period,
            )
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
    def periods(self):
        """Get all available periods (years, semesters)."""
        select_elem = self.soup.select_one("select[name='psAr']")
        return [(x[0], x[1]) for x in iter_options(select_elem)]


    @property
    def latest_period(self):
        """Get the latest timepoint available in dataset."""
        return self.periods[-1]

    def _get_period_id(self, period_label):
        if not hasattr(self, "_period_translattion"):
            self._period_translattion = dict([(x[1], x[0]) for x in self.periods])

        return self._period_translattion[period_label]

    @property
    def soup(self):
        if not hasattr(self, "_soup"):
            self._soup = BeautifulSoup(self.blob, 'html.parser')
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
