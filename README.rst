
This is a scraper for statistical data from the Skolverket's (http://siris.skolverket.se/siris)[SIRIS database]  built on top of the `Statscraper package <https://github.com/jplusplus/statscraper>`.

The scraper is limited to the data avialble through http://siris.skolverket.se/siris/ris.export_stat.form

Install
-------

  pip install siris_scraper


Example usage
-------------

.. code:: python

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


Develop
------

Set up:

  pip install -r requirements.txt

Run tests:

  make tests

Todo
------

- The scraper does not handle "uttag" at the moment. Fetches latest by default.
