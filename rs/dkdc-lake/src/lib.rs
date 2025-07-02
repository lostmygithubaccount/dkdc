use anyhow::Result;
use duckdb::{Connection, Statement};
use dkdc_config::{Config, DUCKLAKE_EXTENSION, SQLITE_EXTENSION};

pub mod files;
pub mod secrets;
pub mod archives;

pub struct Lake {
    connection: Connection,
    config: Config,
}

impl Lake {
    pub fn new() -> Result<Self> {
        let config = Config::new()?;
        Self::with_config(config)
    }
    
    pub fn with_config(config: Config) -> Result<Self> {
        config.ensure_metadata_db()?;
        
        let connection = Connection::open_in_memory()?;
        
        connection.execute_batch(&format!("INSTALL {};", DUCKLAKE_EXTENSION))?;
        connection.execute_batch(&format!("INSTALL {};", SQLITE_EXTENSION))?;
        
        let metadata_path = config.metadata_path();
        let data_path = config.data_path();
        
        connection.execute_batch(&format!(
            "ATTACH '{}' AS metadata;",
            metadata_path.display()
        ))?;
        
        connection.execute_batch(&format!(
            "ATTACH 'ducklake:sqlite:{}' AS data (DATA_PATH '{}', ENCRYPTED);",
            metadata_path.display(),
            data_path.display()
        ))?;
        
        connection.execute_batch("USE data;")?;
        
        Ok(Self { connection, config })
    }
    
    pub fn connection(&self) -> &Connection {
        &self.connection
    }
    
    pub fn config(&self) -> &Config {
        &self.config
    }
    
    pub fn execute(&self, sql: &str) -> Result<()> {
        self.connection.execute_batch(sql)?;
        Ok(())
    }
    
    pub fn prepare(&self, sql: &str) -> Result<Statement> {
        Ok(self.connection.prepare(sql)?)
    }
    
    pub fn get_sql_commands(&self) -> String {
        let metadata_path = self.config.metadata_path();
        let data_path = self.config.data_path();
        
        format!(
            r#"INSTALL {};
INSTALL {};

ATTACH '{}' AS metadata;
ATTACH 'ducklake:sqlite:{}' AS data (DATA_PATH '{}', ENCRYPTED);

USE data;"#,
            DUCKLAKE_EXTENSION,
            SQLITE_EXTENSION,
            metadata_path.display(),
            metadata_path.display(),
            data_path.display()
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_lake_creation() {
        let lake = Lake::new();
        assert!(lake.is_ok());
    }
}