#!/usr/bin/env python3
from subprocess import call
from version import version

call(["python3", "setup.py", "sdist", "bdist_wheel"])
call(["python3", "-m", "twine", "upload", "dist/siris_scraper-{}*".format(version)])
