# imports
import os
import toml
import ibis

import ibis.selectors as s

import logging as log

import plotly.io as pio
import plotly.express as px

from rich import print
from dotenv import load_dotenv
from datetime import datetime, timedelta, date

# configuration
## logger
# log.basicConfig(level=log.INFO)

## config.toml
config = toml.load(os.path.expanduser("~/.dkdc/config.toml"))["eda"]

## load .env file
load_dotenv()
load_dotenv(os.path.expanduser("~/.dkdc/.env"))

## ibis config
ibis.options.interactive = True

# connect to backend
connection_uri = config["connection_uri"]
log.info(f"connection URI: {connection_uri}")
con = ibis.connect(f"{connection_uri}")
tables = con.list_tables()

# setup viz
pio.templates.default = "plotly_dark"

# ai
from dkdc.ai import AI

ai = AI(con)
