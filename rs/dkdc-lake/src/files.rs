use crate::Lake;
use anyhow::Result;
use chrono::{DateTime, Utc};
use dkdc_config::FILES_TABLE_NAME;
use duckdb::params;

pub struct File {
    pub filepath: String,
    pub filename: String,
    pub filedata: Vec<u8>,
    pub filesize: i64,
    pub fileupdated: DateTime<Utc>,
}

impl Lake {
    pub fn create_files_table(&self) -> Result<()> {
        let sql = format!(
            "CREATE TABLE IF NOT EXISTS {} (
                filepath VARCHAR,
                filename VARCHAR,
                filedata BLOB,
                filesize BIGINT,
                fileupdated TIMESTAMP
            )",
            FILES_TABLE_NAME
        );
        self.execute(&sql)?;
        Ok(())
    }

    pub fn add_file(&self, filepath: &str, filename: &str, data: &[u8]) -> Result<()> {
        self.create_files_table()?;

        let sql = format!(
            "INSERT INTO {} (filepath, filename, filedata, filesize, fileupdated)
             VALUES (?, ?, ?, ?, ?)",
            FILES_TABLE_NAME
        );

        let mut stmt = self.prepare(&sql)?;
        stmt.execute(params![
            filepath,
            filename,
            data,
            data.len() as i64,
            Utc::now().to_rfc3339(),
        ])?;

        Ok(())
    }

    pub fn get_file(&self, filepath: &str, filename: &str) -> Result<Option<File>> {
        let sql = format!(
            "SELECT filepath, filename, filedata, filesize, fileupdated
             FROM {}
             WHERE filepath = ? AND filename = ?
             ORDER BY fileupdated DESC
             LIMIT 1",
            FILES_TABLE_NAME
        );

        let mut stmt = self.prepare(&sql)?;
        let mut rows = stmt.query(params![filepath, filename])?;

        if let Some(row) = rows.next()? {
            Ok(Some(File {
                filepath: row.get(0)?,
                filename: row.get(1)?,
                filedata: row.get(2)?,
                filesize: row.get(3)?,
                fileupdated: {
                    // DuckDB returns timestamps as microseconds since epoch
                    let micros: i64 = row.get(4)?;
                    let secs = micros / 1_000_000;
                    let nanos = ((micros % 1_000_000) * 1000) as u32;
                    DateTime::from_timestamp(secs, nanos).unwrap_or_else(Utc::now)
                },
            }))
        } else {
            Ok(None)
        }
    }

    pub fn list_files(&self, filepath: &str) -> Result<Vec<String>> {
        let sql = format!(
            "SELECT DISTINCT filename
             FROM {}
             WHERE filepath = ?
             ORDER BY filename",
            FILES_TABLE_NAME
        );

        let mut stmt = self.prepare(&sql)?;
        let mut rows = stmt.query(params![filepath])?;

        let mut files = Vec::new();
        while let Some(row) = rows.next()? {
            files.push(row.get(0)?);
        }

        Ok(files)
    }

    pub fn delete_file(&self, filepath: &str, filename: &str) -> Result<()> {
        let sql = format!(
            "DELETE FROM {} WHERE filepath = ? AND filename = ?",
            FILES_TABLE_NAME
        );

        let mut stmt = self.prepare(&sql)?;
        stmt.execute(params![filepath, filename])?;

        Ok(())
    }
}
