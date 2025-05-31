# Add Postgres to docker-compose stack

I want a Postgres container named `dkdc-dl-catalog` that I can spinup with `docker compuse up dkdc-dl-catalog`. It should by default pass through to `./pgdata` for the data storage so when I stop the container, the data is persisted.

## DuckLake

DuckLake just released, a lakehouse for DuckDB that can use Postgres as the catalog. See:

- https://ducklake.select/docs/stable/duckdb/usage/choosing_a_catalog_database
- https://duckdb.org/docs/stable/core_extensions/postgres
- `./init.sql` for how I initialize this, and `./dev.py` for some code (see the underlying code as well)

## `dkdc-dl`

Update `dkdc-dl` to based on an env var (DKDC_DL_CATALOG) to use Postgres or what it currently does (sqlite). So as a user I'll:

```
docker compose up dkdc-dl-catalog
DKDC_DL_CATALOG=postgres ./dev.py
```

And have access to the Postgres catalog.

Use `datalake/postgres` and `datalake/sqlite` directories for the data, cleaning up whatever's in there now (all data is example data and can be deleted). This way I can runon the two catalogs in parallel without interfering. also note DKDC_DL_CATALOG=sqlite should be the default but also allowed to be set explicitly basically.

Don't worry about security stuff, this will all run "locally" behind some very secure configurations. The Postgres should be easy to access w/ simple username/password.

