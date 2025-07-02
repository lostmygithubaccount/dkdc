use crate::Lake;
use anyhow::Result;
use dkdc_config::ARCHIVES_TABLE_NAME;
use duckdb::params;

impl Lake {
    pub fn create_archives_table(&self) -> Result<()> {
        let sql = format!(
            "CREATE TABLE IF NOT EXISTS {} (
                filepath VARCHAR,
                filename VARCHAR,
                filedata BLOB,
                filesize BIGINT,
                fileupdated TIMESTAMP
            )",
            ARCHIVES_TABLE_NAME
        );
        self.execute(&sql)?;
        Ok(())
    }

    pub fn add_archive(&self, name: &str, data: &[u8]) -> Result<()> {
        self.create_archives_table()?;

        let sql = format!(
            "INSERT INTO {} (filepath, filename, filedata, filesize, fileupdated)
             VALUES (?, ?, ?, ?, ?)",
            ARCHIVES_TABLE_NAME
        );

        let mut stmt = self.prepare(&sql)?;
        use chrono::Utc;
        stmt.execute(params![
            "./archives",
            name,
            data,
            data.len() as i64,
            Utc::now().to_rfc3339(),
        ])?;

        Ok(())
    }

    pub fn get_archive(&self, name: &str) -> Result<Option<Vec<u8>>> {
        let sql = format!(
            "SELECT filedata
             FROM {}
             WHERE filepath = './archives' AND filename = ?
             ORDER BY fileupdated DESC
             LIMIT 1",
            ARCHIVES_TABLE_NAME
        );

        let mut stmt = self.prepare(&sql)?;
        let mut rows = stmt.query(params![name])?;

        if let Some(row) = rows.next()? {
            Ok(Some(row.get(0)?))
        } else {
            Ok(None)
        }
    }

    pub fn list_archives(&self) -> Result<Vec<String>> {
        let sql = format!(
            "SELECT DISTINCT filename
             FROM {}
             WHERE filepath = './archives'
             ORDER BY filename",
            ARCHIVES_TABLE_NAME
        );

        let mut stmt = self.prepare(&sql)?;
        let mut rows = stmt.query([])?;

        let mut archives = Vec::new();
        while let Some(row) = rows.next()? {
            archives.push(row.get(0)?);
        }

        Ok(archives)
    }
}
