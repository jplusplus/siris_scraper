# encoding: utf-8
"""Tests for browsing the api."""

from siris.scraper import SirisScraper

# Init scraper
scraper = SirisScraper()

# List all schooltypes
verksamhetsformer = scraper.items
# [<Verksamhetsform: 15 (Fritidshem)>, <Verksamhetsform: 10 (Förskola)>, <Verksamhetsform: 14 (Förskoleklass)>,... ]

# Select a schooltype
verksamhetsform = verksamhetsformer.get_by_label(u"Öppen förskola")

# List all available datasets
datasets = verksamhetsform.items
# [<SirisDataset: 40 (Kostnader per kommun)>...]

# Select a dataset
dataset = datasets.get_by_label("Kostnader per kommun")

# Make a query
res = dataset.fetch()  # Get latest available data
#res = dataset.fetch({"period": "2015"})  # Get data for a given period
#res = dataset.fetch({"period": "*"})  # Get data all periods

# List all avilable periods
print(dataset.periods)

# Use the result
# ...in Python Pandas for example
dataframe = res.pandas
