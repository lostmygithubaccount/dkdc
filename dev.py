#!/usr/bin/env -S uvx --with . ipython -i
# ruff: noqa
# Imports
from dkdc_dl import con, ibis

import dkdc

# Variables
bucket = "gs://ascend-io-gcs-public"
feedback_ascenders_glob = "ottos-expeditions/lakev0/generated/events/feedback_ascenders.parquet/year=*/month=*/day=*/*.parquet"
