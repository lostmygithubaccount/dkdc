#!/usr/bin/env duckdb -init
INSTALL ducklake;
INSTALL sqlite;

ATTACH 'ducklake:sqlite:dl.sqlite' AS dl
    (DATA_PATH 'datalake/');
USE dl;
