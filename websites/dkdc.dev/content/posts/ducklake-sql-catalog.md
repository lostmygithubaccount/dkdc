+++
title = "Exploring DuckLake: SQL Databases as Data Catalogs"
date = "2025-06-01"
author = "Cody"
tags = ["ducklake", "data-catalog", "sql", "lakehouse", "duckdb", "delta-lake", "iceberg"]
draft = true
+++

***DuckLake just launched - a new data lake format that stores metadata in SQL databases instead of files. Let's explore what this means and why it's interesting.***

---

I've been experimenting with DuckLake, a recently released data lake format that takes a fundamentally different approach to metadata management. Instead of storing table metadata as JSON files in object storage (like Delta Lake and Iceberg), DuckLake uses SQL databases as the catalog.

The setup is remarkably simple:

```sql
-- Install the DuckLake extension
INSTALL ducklake;

-- Attach a catalog using PostgreSQL
ATTACH 'ducklake:postgres:host=localhost port=5432 dbname=ducklake user=dkdc password=dkdc' AS dl
    (DATA_PATH 'datalake/catalog-postgres/');

-- Or use SQLite for local development  
ATTACH 'ducklake:sqlite:dl.sqlite' AS dl
    (DATA_PATH 'datalake/catalog-sqlite/');

USE dl;
```

This is exactly the setup I'm using in my [dkdc-dl package](https://github.com/lostmygithubaccount/dkdc) - a simple abstraction that lets me switch between SQLite for local development and PostgreSQL for more serious work.

But why does this architectural choice matter? Let's dive into the technical implications.

## Understanding the architectural difference

To understand why DuckLake's approach is interesting, let's first look at how traditional lakehouses handle metadata.

Traditional formats like Delta Lake and Iceberg store metadata as files in object storage. Every table operation - adding files, updating schema, creating snapshots - writes new JSON files to a `_delta_log/` or metadata directory. This works, but creates some interesting challenges.

DuckLake takes a different approach: metadata lives in a SQL database, while data remains in standard Parquet files in object storage. This architectural split enables some compelling capabilities:

{% mermaid() %}
flowchart TB
    subgraph "DuckLake Architecture"
        subgraph "Metadata Layer"
            CATALOG[(PostgreSQL/MySQL/SQLite<br/>Catalog Database)]
            T1[ducklake_tables]
            T2[ducklake_files]
            T3[ducklake_snapshots]
            T4[ducklake_statistics]
            
            CATALOG --> T1
            CATALOG --> T2
            CATALOG --> T3
            CATALOG --> T4
        end
        
        subgraph "Data Layer"
            S3[(S3/GCS/Azure<br/>Parquet Files)]
        end
        
        subgraph "Compute Layer"
            DUCK1[DuckDB Instance 1]
            DUCK2[DuckDB Instance 2]
            DUCK3[DuckDB Instance N]
        end
    end
    
    T2 -.->|"References"| S3
    DUCK1 <--> CATALOG
    DUCK2 <--> CATALOG
    DUCK3 <--> CATALOG
    DUCK1 <--> S3
    DUCK2 <--> S3
    DUCK3 <--> S3
    
    style CATALOG fill:#1a1a2e,stroke:#9d4edd,stroke-width:3px,color:#fff
    style S3 fill:#16213e,stroke:#c77dff,stroke-width:3px,color:#fff
    style DUCK1 fill:#0f3460,stroke:#7209b7,stroke-width:2px,color:#e0aaff
    style DUCK2 fill:#0f3460,stroke:#7209b7,stroke-width:2px,color:#e0aaff
    style DUCK3 fill:#0f3460,stroke:#7209b7,stroke-width:2px,color:#e0aaff
{% end %}

## The many small files challenge

One problem that's particularly interesting to explore is the "many small files" issue. Streaming data systems naturally create lots of small files:

{% mermaid() %}
flowchart TB
    subgraph "Streaming Data Reality"
        STREAM[Kafka Stream] --> WRITER[Spark Streaming<br/>5 min micro-batches]
        WRITER --> D1[2024/01/01/00/part-001.parquet<br/>100KB]
        WRITER --> D2[2024/01/01/00/part-002.parquet<br/>100KB]
        WRITER --> D3[2024/01/01/05/part-001.parquet<br/>100KB]
        WRITER --> DOTS1[...]
        WRITER --> D4[2024/01/01/23/part-999.parquet<br/>100KB]
    end
    
    subgraph "One Day Later"
        TOTAL[288 directories<br/>x 10 files each<br/>= 2,880 files<br/>for ONE DAY]
    end
    
    subgraph "Query Time Horror"
        QUERY[SELECT * FROM events<br/>WHERE date = '2024-01-01'] --> LIST[S3 LIST operations]
        LIST --> PAIN[😱 2,880 API calls<br/>~30 seconds just to list]
        PAIN --> READ[Read 2,880 files<br/>More API calls]
        READ --> RESULT[288MB of actual data<br/>2 minutes total]
    end
    
    D4 -.->|"multiply by 365 days"| TOTAL
    TOTAL --> QUERY
    
    style STREAM fill:#1a1a2e,stroke:#9d4edd,stroke-width:2px,color:#e0aaff
    style PAIN fill:#3c1361,stroke:#ff006e,stroke-width:3px,color:#fff
    style TOTAL fill:#2d1b69,stroke:#ff006e,stroke-width:2px,color:#fff
{% end %}

This pattern emerges because:
- Object storage doesn't support appending to existing files
- Streaming systems write data as it arrives
- Each write operation creates a new file

The consequences include:
- More S3 LIST/GET operations during query planning
- Longer query planning times
- Higher storage API costs
- Degraded query performance

## How file-based metadata works

To understand DuckLake's approach, let's look at how Delta Lake manages metadata:

{% mermaid() %}
flowchart LR
    subgraph "Delta Lake Metadata Chaos"
        subgraph "_delta_log/"
            J1[00000000000000000000.json<br/>Table creation]
            J2[00000000000000000001.json<br/>Add files]
            J3[00000000000000000002.json<br/>Update stats]
            J4[...]
            J5[00000000000000000999.json<br/>More changes]
            CP[00000000000000001000.checkpoint.parquet<br/>Checkpoint]
            J6[00000000000000001001.json<br/>More changes after checkpoint]
        end
    end
    
    subgraph "To Read Table State"
        READ[Read Latest Checkpoint] --> SCAN[Scan all JSONs<br/>after checkpoint]
        SCAN --> PARSE[Parse & merge<br/>all operations]
        PARSE --> STATE[Current table state]
    end
    
    J1 -.->|"Sequential reads required"| READ
    CP --> READ
    J6 --> SCAN
    
    style J1 fill:#2d1b69,stroke:#ff006e,stroke-width:1px,color:#fff
    style J2 fill:#2d1b69,stroke:#ff006e,stroke-width:1px,color:#fff
    style J3 fill:#2d1b69,stroke:#ff006e,stroke-width:1px,color:#fff
    style J5 fill:#2d1b69,stroke:#ff006e,stroke-width:1px,color:#fff
    style J6 fill:#2d1b69,stroke:#ff006e,stroke-width:1px,color:#fff
    style CP fill:#1a1a2e,stroke:#9d4edd,stroke-width:2px,color:#e0aaff
    style PARSE fill:#3c1361,stroke:#ff006e,stroke-width:2px,color:#fff
{% end %}

Every operation creates a new JSON file. Want to know the current state of your table? You need to:
1. Find the latest checkpoint (Parquet file)
2. List all JSON files after that checkpoint
3. Download and parse each one sequentially
4. Apply all operations in order

This is essentially a transaction log implemented on object storage - a pattern that's well-understood in database systems.

## Handling concurrent writes

File-based systems typically use optimistic concurrency control:

{% mermaid() %}
flowchart TB
    subgraph "Delta Lake Concurrent Write 'Strategy'"
        W1[Writer 1] --> CHECK1[Read _delta_log/]
        W2[Writer 2] --> CHECK2[Read _delta_log/]
        
        CHECK1 --> CONFLICT{Who wins?}
        CHECK2 --> CONFLICT
        
        CONFLICT -->|"Optimistic concurrency"| RETRY1[Writer 1 retries]
        CONFLICT -->|"Hope for the best"| RETRY2[Writer 2 retries]
        
        RETRY1 --> FAIL1[Still conflicts?<br/>Exponential backoff]
        RETRY2 --> FAIL2[Eventually fails]
    end
    
    subgraph "What Actually Happens"
        REALITY[One writer succeeds<br/>Others waste compute<br/>No real coordination]
    end
    
    FAIL1 --> REALITY
    FAIL2 --> REALITY
    
    style CONFLICT fill:#3c1361,stroke:#ff006e,stroke-width:3px,color:#fff
    style REALITY fill:#2d1b69,stroke:#ff006e,stroke-width:2px,color:#fff
{% end %}

This optimistic approach can work well, but under high concurrency it can lead to retry cascades where multiple writers compete and back off.

## DuckLake's approach

DuckLake takes a different path: store metadata in a SQL database.

{% mermaid() %}
flowchart TB
    subgraph "DuckLake Architecture"
        subgraph "Metadata (SQL DB)"
            CATALOG[(PostgreSQL/MySQL/SQLite<br/>Catalog Database)]
            T1[ducklake_tables]
            T2[ducklake_files]
            T3[ducklake_snapshots]
            T4[ducklake_statistics]
            
            CATALOG --> T1
            CATALOG --> T2
            CATALOG --> T3
            CATALOG --> T4
        end
        
        subgraph "Data (Object Storage)"
            S3[(S3/GCS/Azure<br/>Parquet Files Only)]
        end
        
        subgraph "Compute"
            DUCK1[DuckDB Instance 1]
            DUCK2[DuckDB Instance 2]
            DUCK3[DuckDB Instance N]
        end
    end
    
    T2 -.->|"References"| S3
    DUCK1 <--> CATALOG
    DUCK2 <--> CATALOG
    DUCK3 <--> CATALOG
    DUCK1 <--> S3
    DUCK2 <--> S3
    DUCK3 <--> S3
    
    style CATALOG fill:#1a1a2e,stroke:#9d4edd,stroke-width:3px,color:#fff
    style S3 fill:#16213e,stroke:#c77dff,stroke-width:3px,color:#fff
    style DUCK1 fill:#0f3460,stroke:#7209b7,stroke-width:2px,color:#e0aaff
    style DUCK2 fill:#0f3460,stroke:#7209b7,stroke-width:2px,color:#e0aaff
    style DUCK3 fill:#0f3460,stroke:#7209b7,stroke-width:2px,color:#e0aaff
{% end %}

This creates a clean separation:
- **Metadata**: Managed by proven SQL database systems
- **Data**: Standard Parquet files in object storage
- **Compute**: DuckDB instances that connect to both

## Trying it out

Here's the setup I'm using in my experiments:

```sql
-- Install the extension
INSTALL ducklake;

-- For local development with SQLite
ATTACH 'ducklake:sqlite:dl.sqlite' AS dl
    (DATA_PATH 'datalake/catalog-sqlite/');

-- For testing with PostgreSQL
ATTACH 'ducklake:postgres:host=localhost port=5432 dbname=ducklake user=dkdc password=dkdc' AS dl
    (DATA_PATH 'datalake/catalog-postgres/');

USE dl;
```

This matches exactly what I have in my [dkdc-dl package](https://github.com/lostmygithubaccount/dkdc) - environment-driven catalog selection.

## What makes this interesting

With metadata in a SQL database, certain operations become straightforward:

```sql
BEGIN TRANSACTION;

-- Add new data files
INSERT INTO ducklake_files (table_id, file_path, row_count, size_bytes)
VALUES 
    (1, 's3://bucket/table1/part-001.parquet', 1000000, 50000000),
    (1, 's3://bucket/table1/part-002.parquet', 1000000, 50000000);

-- Update table statistics
UPDATE ducklake_statistics 
SET total_rows = total_rows + 2000000,
    total_size = total_size + 100000000
WHERE table_id = 1;

-- Create a new snapshot
INSERT INTO ducklake_snapshots (table_id, snapshot_id, timestamp)
VALUES (1, gen_random_uuid(), NOW());

COMMIT;
```

If anything fails, the whole transaction rolls back. No partial states. No corruption. No manual cleanup.

## Concurrent writes at scale

Multiple writers? PostgreSQL has been solving this for 30 years:

{% mermaid() %}
flowchart LR
    subgraph "DuckLake Concurrent Writes"
        W1[Writer 1] --> TX1[BEGIN TRANSACTION]
        W2[Writer 2] --> TX2[BEGIN TRANSACTION]
        W3[Writer 3] --> TX3[BEGIN TRANSACTION]
        
        TX1 --> DB[(PostgreSQL)]
        TX2 --> DB
        TX3 --> DB
        
        DB --> MAGIC[MVCC Magic ✨<br/>Row-level locking<br/>Deadlock detection<br/>Automatic retry]
        
        MAGIC --> SUCCESS[All writers succeed<br/>No conflicts<br/>Consistent state]
    end
    
    style DB fill:#1a1a2e,stroke:#9d4edd,stroke-width:3px,color:#fff
    style MAGIC fill:#16213e,stroke:#c77dff,stroke-width:2px,color:#e0aaff
    style SUCCESS fill:#0f3460,stroke:#7209b7,stroke-width:2px,color:#e0aaff
{% end %}

Database MVCC (Multi-Version Concurrency Control) provides:
- True isolation between writers
- Automatic conflict resolution
- No wasted compute on retries
- Consistent, predictable behavior

## Lightning-fast metadata queries

Want to find all tables modified in the last week with more than 1 billion rows?

```sql
-- DuckLake: Just SQL
SELECT 
    t.table_name,
    t.created_at,
    s.total_rows / 1e9 as billions_of_rows,
    s.total_size / 1e12 as size_tb,
    COUNT(DISTINCT f.file_path) as file_count
FROM ducklake_tables t
JOIN ducklake_statistics s ON t.table_id = s.table_id
JOIN ducklake_files f ON t.table_id = f.table_id
WHERE t.modified_at > NOW() - INTERVAL '7 days'
  AND s.total_rows > 1e9
GROUP BY t.table_id, t.table_name, t.created_at, s.total_rows, s.total_size
ORDER BY s.total_rows DESC;
```

With file-based catalogs, this query would require:
1. Listing thousands of metadata files
2. Downloading and parsing each one
3. Building statistics in memory
4. Filtering and sorting locally

DuckLake? One indexed SQL query. Milliseconds.

## Effortless time travel

DuckLake's time travel is just timestamp queries:

```sql
-- View table as of specific time
SELECT * FROM my_table 
AS OF TIMESTAMP '2024-01-01 00:00:00';

-- Find what changed between snapshots
SELECT 
    f.file_path,
    f.operation,
    f.timestamp
FROM ducklake_file_history f
WHERE f.table_id = 1
  AND f.timestamp BETWEEN '2024-01-01' AND '2024-01-02'
ORDER BY f.timestamp;

-- Rollback to previous snapshot
UPDATE ducklake_tables
SET current_snapshot_id = (
    SELECT snapshot_id 
    FROM ducklake_snapshots 
    WHERE table_id = 1 
      AND timestamp < '2024-01-01'
    ORDER BY timestamp DESC 
    LIMIT 1
)
WHERE table_id = 1;
```

No parsing transaction logs. No reconstructing state. Just indexed timestamp lookups.

## The small files problem: solved

DuckLake elegantly solves this with intelligent buffering:

{% mermaid() %}
flowchart TB
    subgraph "DuckLake Streaming Solution"
        STREAM[Kafka Stream] --> BUFFER[In-Memory Buffer<br/>or Temp Storage]
        
        BUFFER --> DECISION{Size/Time<br/>Threshold?}
        
        DECISION -->|"< 100MB AND < 5min"| WAIT[Keep buffering]
        DECISION -->|">= 100MB OR >= 5min"| WRITE[Write single<br/>Parquet file]
        
        WAIT --> BUFFER
        
        WRITE --> S3[(S3: Fewer,<br/>larger files)]
        WRITE --> CATALOG[(SQL: Single<br/>INSERT statement)]
    end
    
    subgraph "Query Performance"
        QUERY[SELECT * FROM events] --> CATALOG
        CATALOG --> PLAN[Query plan:<br/>10 files instead of 2,880]
        PLAN --> S3
        S3 --> FAST[⚡ 2 seconds<br/>vs 2 minutes]
    end
    
    style BUFFER fill:#16213e,stroke:#c77dff,stroke-width:2px,color:#e0aaff
    style CATALOG fill:#1a1a2e,stroke:#9d4edd,stroke-width:3px,color:#fff
    style S3 fill:#0f3460,stroke:#7209b7,stroke-width:2px,color:#e0aaff
    style FAST fill:#16213e,stroke:#7209b7,stroke-width:3px,color:#fff
{% end %}

This approach delivers:
- **Fewer, larger files**: Better query performance
- **Single SQL transactions**: Atomic metadata updates
- **Reduced API costs**: Fewer S3 operations
- **Faster queries**: Orders of magnitude improvement

## Production architecture that scales

Here's a real production DuckLake setup:

{% mermaid() %}
flowchart TB
    subgraph "Production DuckLake Architecture"
        subgraph "Ingest Layer"
            K1[Kafka] --> FLINK[Flink/Spark<br/>Streaming]
            API[REST APIs] --> BATCH[Batch ETL]
            DB[Databases] --> CDC[CDC Streams]
        end
        
        subgraph "Write Path"
            FLINK --> WRITER[DuckDB Writers<br/>Auto-scaling pods]
            BATCH --> WRITER
            CDC --> WRITER
            
            WRITER --> PG[(PostgreSQL<br/>Primary)]
            WRITER --> S3[(S3 Data Lake)]
            
            PG --> PGREP[(PostgreSQL<br/>Read Replicas)]
        end
        
        subgraph "Read Path"
            ANALYST[Analysts] --> NOTEBOOK[Notebooks/<br/>DuckDB CLI]
            BI[BI Tools] --> DUCKAPI[DuckDB<br/>API Servers]
            APP[Applications] --> DUCKAPI
            
            NOTEBOOK --> PGREP
            NOTEBOOK --> S3
            DUCKAPI --> PGREP
            DUCKAPI --> S3
        end
        
        subgraph "Operations"
            PGREP --> BACKUP[Automated<br/>PG Backups]
            S3 --> LIFECYCLE[S3 Lifecycle<br/>Policies]
            PG --> MONITOR[Standard PG<br/>Monitoring]
        end
    end
    
    style PG fill:#1a1a2e,stroke:#9d4edd,stroke-width:3px,color:#fff
    style S3 fill:#16213e,stroke:#c77dff,stroke-width:3px,color:#fff
    style WRITER fill:#0f3460,stroke:#7209b7,stroke-width:2px,color:#e0aaff
    style DUCKAPI fill:#0f3460,stroke:#7209b7,stroke-width:2px,color:#e0aaff
{% end %}

This architecture leverages proven technologies:
- **PostgreSQL**: Battle-tested reliability and performance
- **Object storage**: Infinite scale and durability
- **DuckDB**: High-performance analytical processing
- **Standard protocols**: No vendor lock-in

## Migration is refreshingly simple

Have an existing Delta Lake? Migration script:

```python
import duckdb
from deltalake import DeltaTable

# Read Delta Lake metadata
dt = DeltaTable("s3://bucket/delta-table")
files = dt.files()
schema = dt.schema().json()
history = dt.history()

# Connect to DuckLake
con = duckdb.connect()
con.execute("INSTALL ducklake")
con.execute("""
    ATTACH 'ducklake:postgres:...' AS new_lake 
    (DATA_PATH 's3://bucket/ducklake/')
""")

# Migrate metadata (one transaction!)
con.execute("BEGIN")

# Create table
con.execute(f"""
    CREATE TABLE new_lake.{table_name} 
    AS SELECT * FROM 's3://bucket/delta-table/*.parquet' 
    WHERE 1=0
""")

# Register existing Parquet files  
for file in files:
    con.execute("""
        INSERT INTO ducklake_files 
        (table_id, file_path, row_count, size_bytes)
        VALUES (?, ?, ?, ?)
    """, [table_id, file, count, size])

# Migrate history
for entry in history:
    con.execute("""
        INSERT INTO ducklake_history ...
    """)

con.execute("COMMIT")
```

Your Parquet files don't move. You're just moving metadata from JSON files to a database.

## Why this approach matters

Using SQL databases for metadata management brings several theoretical advantages:

### Transactional consistency
Database transactions provide ACID guarantees that are difficult to achieve with file-based approaches. Multiple metadata operations can be atomically committed or rolled back.

### Query capabilities
Metadata becomes queryable with full SQL. Want to find all tables with more than 1 billion rows? That's a simple WHERE clause instead of parsing thousands of files.

### Concurrent access
Databases have sophisticated mechanisms for handling concurrent reads and writes that have been refined over decades.

### Operational tooling
Standard database operations (backup, monitoring, replication) work out of the box.

## What this means for data infrastructure

DuckLake's approach suggests an interesting architectural pattern: using purpose-built components for what they do best, rather than implementing everything on object storage.

- **Databases**: Excellent at metadata management, transactions, queries
- **Object storage**: Excellent at scale, durability, cost
- **Analytics engines**: Excellent at processing columnar data

This separation of concerns could lead to simpler, more composable data systems.

## Trade-offs to consider

**Additional infrastructure complexity**: You now need to manage a database in addition to object storage.

**Catalog availability**: Your catalog database becomes a potential single point of failure (though databases have well-understood HA patterns).

**Cross-region considerations**: If your storage and catalog are in different regions, latency could be a factor.

**Metadata scale**: While PostgreSQL can handle billions of rows, very large catalogs might need different approaches.

## Trying it yourself

Here's a simple example to explore DuckLake:

```bash
# Install DuckDB
pip install duckdb

# Create a basic DuckLake setup
python -c "
import duckdb

con = duckdb.connect()
con.execute('INSTALL ducklake')
con.execute(\"\"\"
    ATTACH 'ducklake:sqlite:demo.db' AS demo_lake 
    (DATA_PATH './demo_data/')
\"\"\")

# Create a simple table
con.execute(\"\"\"
    CREATE TABLE demo_lake.test_table AS 
    SELECT range AS id, 'test_' || range AS name
    FROM range(100)
\"\"\")

# Query it
result = con.execute('SELECT COUNT(*) FROM demo_lake.test_table').fetchone()
print(f'Rows: {result[0]}')
"
```

## Interesting implications

DuckLake's approach highlights an interesting principle: use the right tool for the job. Instead of building everything on object storage, it:

- Uses databases for what they're good at (metadata, transactions, queries)
- Uses object storage for what it's good at (scale, durability, cost)
- Uses analytical engines for what they're good at (processing data)

This separation could enable simpler, more composable data architectures where each component does what it does best.

## What's compelling about this

I find DuckLake interesting because it challenges some assumptions about data lake architectures. The idea that metadata *must* live in object storage alongside data isn't necessarily true. 

By using SQL databases for catalog management, you get decades of database innovation for free: ACID transactions, sophisticated query optimization, operational tooling, and well-understood scaling patterns.

Whether this approach will prove superior in practice remains to be seen, but it's a fascinating architectural experiment that's worth watching.

---

*Currently experimenting with DuckLake in my [dkdc project](https://github.com/lostmygithubaccount/dkdc). The simplicity is refreshing.*