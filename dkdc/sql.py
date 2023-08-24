# imports
import os
import toml
import ibis
import typer
import marvin
import requests

import logging as log

from rich import console

from marvin import ai_fn, ai_model
from pydantic import BaseModel, Field
from marvin.engine.language_models import chat_llm

## local imports
from dkdc.common import dkdcai

# variables
console = console.Console()

marvin.settings.llm_model = "azure_openai/gpt-4"


def _get_schema(t):
    return str(t.schema()).replace("ibis.Schema ", " ")


def sql(
    table_name: str = None,
    database: str = "cache.ddb",
    instructions: str = "summarize the table",
) -> str:
    con = ibis.duckdb.connect(database, read_only=True)
    t = con.table(table_name)
    return (
        _sql(t, _get_schema(t), instructions)
        .strip(";")
        .replace("table_name", table_name)
    )


@ai_fn
def _sql(
    table_name: str, schema: str = None, instructions: str = "summarize the table"
) -> str:
    """Return the DuckDB SQL query for the given instructions on the given table_name with the given schema

    Use 'FROM <table_name>' to specify the table to query from.

    Interpret what the user wants and generate the simplest SQL query.
    """
