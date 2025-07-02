use anyhow::Result;
use dkdc_config::{Config, DKDC_BANNER};
use dkdc_lake::Lake;
use std::process::Command;

pub enum DevMode {
    Sql,
    Python,
}

pub struct Dev {
    lake: Lake,
    config: Config,
}

impl Dev {
    pub fn new() -> Result<Self> {
        let config = Config::new()?;
        let lake = Lake::with_config(config.clone())?;
        Ok(Self { config, lake })
    }

    pub fn with_config(config: Config) -> Result<Self> {
        let lake = Lake::with_config(config.clone())?;
        Ok(Self { config, lake })
    }

    pub fn check_duckdb(&self) -> Result<bool> {
        let output = Command::new("which").arg("duckdb").output()?;
        Ok(output.status.success())
    }

    pub fn launch(&self, mode: DevMode) -> Result<()> {
        match mode {
            DevMode::Sql => self.launch_sql(),
            DevMode::Python => self.launch_python(),
        }
    }

    pub fn launch_sql(&self) -> Result<()> {
        if !self.check_duckdb()? {
            anyhow::bail!(
                "DuckDB CLI not found. Install with: curl https://install.duckdb.org | sh"
            );
        }

        println!("{}", DKDC_BANNER);
        println!("\n=== dkdc dev (SQL) ===");
        println!("Connected to DuckLake database");
        println!("Database: my_ducklake\n");

        let sql_commands = self.lake.get_sql_commands();

        let status = Command::new("duckdb")
            .arg("-cmd")
            .arg(&sql_commands)
            .status()?;

        if !status.success() {
            anyhow::bail!("DuckDB CLI exited with error");
        }

        Ok(())
    }

    pub fn launch_python(&self) -> Result<()> {
        // Ensure Python environment is set up
        self.ensure_python_env()?;
        
        println!("{}", DKDC_BANNER);
        println!("\n=== dkdc dev (Python) ===");
        println!("Connected to DuckLake database");
        println!("Database: my_ducklake");
        println!("Namespace: ibis, con, metacon, files, secrets\n");
        
        // Get the SQL commands for DuckLake setup
        let sql_commands = self.lake.get_sql_commands();
        
        // Launch IPython with our setup
        self.launch_ipython_with_duckdb(&sql_commands)?;
        
        Ok(())
    }
    
    fn ensure_python_env(&self) -> Result<()> {
        let venv_path = self.config.venv_path();
        
        if !venv_path.exists() {
            println!("Setting up Python environment...");
            
            // Check if uv is available
            let uv_check = Command::new("which")
                .arg("uv")
                .output()?;
                
            if !uv_check.status.success() {
                anyhow::bail!("uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh");
            }
            
            // Create virtual environment
            let status = Command::new("uv")
                .args(&["venv", venv_path.to_str().unwrap()])
                .status()?;
                
            if !status.success() {
                anyhow::bail!("Failed to create virtual environment");
            }
            
            println!("Installing required packages...");
            
            let packages = vec!["ipython", "duckdb", "ibis-framework[duckdb]"];
            
            for package in packages {
                println!("  Installing {}...", package);
                let status = Command::new("uv")
                    .args(&["pip", "install", "--python", venv_path.to_str().unwrap(), package])
                    .status()?;
                    
                if !status.success() {
                    anyhow::bail!("Failed to install {}", package);
                }
            }
        }
        
        Ok(())
    }
    
    fn launch_ipython_with_duckdb(&self, sql_commands: &str) -> Result<()> {
        let python_path = self.config.python_path();
        
        // Create a Python script that sets up the environment and launches IPython
        let setup_script = format!(
            r#"
import ibis
import duckdb
from IPython import start_ipython

# Create ibis connection (in-memory)
con = ibis.duckdb.connect()

# Get the raw DuckDB connection
con_duckdb = con.con

# Execute SQL commands to set up DuckLake
sql_commands = '''{}'''
for cmd in sql_commands.strip().split(';'):
    if cmd.strip():
        con.raw_sql(cmd.strip())

# Configure ibis
ibis.options.interactive = True
ibis.options.repr.interactive.max_rows = 40

# Set ibis as default backend
ibis.set_backend(con)

# Create metadata connection placeholder
metacon = None  # TODO: Connect to metadata SQLite

# Prepare namespace
namespace = {{
    'ibis': ibis,
    'con': con,
    'duckdb': duckdb,
    'con_duckdb': con_duckdb,
    'metacon': metacon,
}}

# Add dkdc modules placeholder
# TODO: Add files and secrets modules

# Start IPython with our namespace
start_ipython(argv=['--no-banner'], user_ns=namespace)
"#,
            sql_commands
        );
        
        // Write the script to a temporary file
        let temp_script = self.config.dkdc_dir().join("dev_setup.py");
        std::fs::write(&temp_script, setup_script)?;
        
        // Launch Python with the script
        let status = Command::new(python_path)
            .arg(temp_script)
            .status()?;
            
        if !status.success() {
            anyhow::bail!("IPython exited with error");
        }
        
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dev_creation() {
        let dev = Dev::new();
        assert!(dev.is_ok());
    }
}
