# encoding:utf-8
import re
from copy import deepcopy
from bs4 import BeautifulSoup
from bs4.element import Tag

def parse_period(period_str):
    """

    Example usage:
    ```
    parse_period("Valt år: 2016 Endast kommunal huvudman")
    # ("2016", "år")

    parse_period("Valt läsår: 2016/17 ")
    # ("2016/17", "läsår")

    parse_period("Vald termin: HT12")
    # ("HT12", "termin")
    ```

    """
    reg_ex = u"Val[dt] ([åäö\w]+): ([\w/]+)[\s]?"
    periodicity, period = re.match(reg_ex, period_str).groups()

    return period, periodicity



def iter_options(select_html):
    """The html structure is malformated in select tags.
    Resort to parsing with regex.

    :param select_html: string or soup tag
    """
    # Regex parsing value and label from option tags
    option_reg_ex = 'value="([\d\w]+)">([\w\såäöÅÄÖ,///-]+)\\n'
    if isinstance(select_html, Tag):
        select_html = str(select_html)

    options = re.findall(option_reg_ex, str(select_html))
    for value, label in options:
        yield value, label


def get_data_from_xml(xml_data):
    """Yield all single datapoints in an xml file as dicts.

    :param xml (str): xml data as string
    """
    soup = BeautifulSoup(xml_data.replace("\n",""), 'xml')
    root = soup.select_one("root")

    # <inledning>Valt år: 2016 Endast kommunal huvudman</inledning>
    # => (2016, år)
    period, periodicity = parse_period(root.select_one("inledning").text)
    try:
        uttag = root.select_one("leg_uttag").text
    except AttributeError:
        # All dataset do not have "uttag" property
        uttag = None

    for unit_tag in root.select("skola"):
        # Example of tag:
        #<skola kommun_namn="Överkalix" kommunkod="2513" huvudman="Kommunal">
        #    <antal_elever>20</antal_elever>
        #    <totalt>1 688</totalt>
        #    <undervisning>909</undervisning>
        #    <totalt_elev>84 400</totalt_elev>
        #    <undervisning_elev>45 500</undervisning_elev>
        #    <lokaler_elev>11 200</lokaler_elev>
        #</skola>
        base_data = {
            "period": period,
            "periodicity": periodicity,
            "uttag": uttag,
        }

        # {'kommunkod': u'1440', 'huvudman': u'Kommunal', 'kommun_namn': u'Ale'}
        base_data.update(unit_tag.attrs)

        for variable in unit_tag.children:
            data = deepcopy(base_data)
            data["variable"] = variable.name
            value, status = parse_value(variable.text)
            data["value"] = value
            data["status"] = status  #
            yield data


def get_metadata_from_xml(xml_data):
    """Get metadata from xml file

    :param xml (str): xml data as string
    """
    raise NotImplementedError()


def parse_value(val):
    """Parse value from cell.
    :returns (tuple): (value, status)
    """
    if val == ".":
        return None, "missing or 0"
    elif val == "..":
        return None, "too few"
    else:
        return float(val.replace(",",".").replace(" ", "")), None
