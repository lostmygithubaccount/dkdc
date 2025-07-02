use crate::Lake;
use anyhow::Result;
use dkdc_config::SECRETS_TABLE_NAME;
use duckdb::params;

impl Lake {
    pub fn create_secrets_table(&self) -> Result<()> {
        let sql = format!(
            "CREATE TABLE IF NOT EXISTS {} (
                filepath VARCHAR,
                filename VARCHAR,
                filedata BLOB,
                filesize BIGINT,
                fileupdated TIMESTAMP
            )",
            SECRETS_TABLE_NAME
        );
        self.execute(&sql)?;
        Ok(())
    }

    pub fn set_secret(&self, name: &str, value: &[u8]) -> Result<()> {
        let sql = format!(
            "INSERT INTO {} (filepath, filename, filedata, filesize, fileupdated)
             VALUES (?, ?, ?, ?, ?)",
            SECRETS_TABLE_NAME
        );

        let mut stmt = self.prepare(&sql)?;
        use chrono::Utc;
        stmt.execute(params![
            "./secrets",
            name,
            value,
            value.len() as i64,
            Utc::now().to_rfc3339(),
        ])?;

        Ok(())
    }

    pub fn get_secret(&self, name: &str) -> Result<Option<Vec<u8>>> {
        let sql = format!(
            "SELECT filedata
             FROM {}
             WHERE filepath = './secrets' AND filename = ?
             ORDER BY fileupdated DESC
             LIMIT 1",
            SECRETS_TABLE_NAME
        );

        let mut stmt = self.prepare(&sql)?;
        let mut rows = stmt.query(params![name])?;

        if let Some(row) = rows.next()? {
            Ok(Some(row.get(0)?))
        } else {
            Ok(None)
        }
    }

    pub fn list_secrets(&self) -> Result<Vec<String>> {
        let sql = format!(
            "SELECT DISTINCT filename
             FROM {}
             WHERE filepath = './secrets'
             ORDER BY filename",
            SECRETS_TABLE_NAME
        );

        let mut stmt = self.prepare(&sql)?;
        let mut rows = stmt.query([])?;

        let mut secrets = Vec::new();
        while let Some(row) = rows.next()? {
            secrets.push(row.get(0)?);
        }

        Ok(secrets)
    }

    pub fn delete_secret(&self, name: &str) -> Result<bool> {
        let sql = format!(
            "DELETE FROM {} WHERE filepath = './secrets' AND filename = ?",
            SECRETS_TABLE_NAME
        );

        let mut stmt = self.prepare(&sql)?;
        let count = stmt.execute(params![name])?;

        Ok(count > 0)
    }
}
