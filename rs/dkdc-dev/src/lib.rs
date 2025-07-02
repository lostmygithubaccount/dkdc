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
        println!("Connected to DuckLake database\n");

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

        // Ensure metadata database exists
        self.config.ensure_metadata_db()?;

        println!("{}", DKDC_BANNER);
        println!("\n=== dkdc dev (Python) ===");
        println!("Connected to DuckLake database");

        // Get the SQL commands for DuckLake setup
        let sql_commands = self.lake.get_sql_commands();

        // Launch IPython with our setup
        self.launch_ipython_with_duckdb(&sql_commands)?;

        Ok(())
    }

    pub fn ensure_python_env(&self) -> Result<()> {
        let venv_path = self.config.venv_path();

        // Check if uv is available
        if !self.check_uv_available()? {
            anyhow::bail!(
                "uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
            );
        }

        // Create virtual environment if it doesn't exist
        if !venv_path.exists() {
            println!("Creating Python environment...");
            self.create_venv(&venv_path)?;
        }

        // Install required packages
        println!("Setting up Python packages...");
        self.install_packages(&venv_path)?;

        Ok(())
    }

    fn check_uv_available(&self) -> Result<bool> {
        Ok(Command::new("which")
            .arg("uv")
            .output()
            .map(|output| output.status.success())
            .unwrap_or(false))
    }

    fn create_venv(&self, venv_path: &std::path::Path) -> Result<()> {
        let status = Command::new("uv")
            .args(["venv", venv_path.to_str().unwrap()])
            .status()?;

        if !status.success() {
            anyhow::bail!("Failed to create virtual environment");
        }

        Ok(())
    }

    fn install_packages(&self, venv_path: &std::path::Path) -> Result<()> {
        const PACKAGES: &[&str] = &["ipython", "duckdb==1.3.1", "ibis-framework[duckdb,sqlite]"];

        for package in PACKAGES {
            let status = Command::new("uv")
                .args([
                    "pip",
                    "install",
                    "--python",
                    venv_path.to_str().unwrap(),
                    package,
                ])
                .status()?;

            if !status.success() {
                anyhow::bail!("Failed to install {}", package);
            }
        }

        Ok(())
    }

    fn launch_ipython_with_duckdb(&self, sql_commands: &str) -> Result<()> {
        let python_path = self.config.python_path();
        let metadata_path = self.config.metadata_path();

        // Create the setup code that will be executed via IPython's -c flag
        let setup_code = format!(
            r#"import ibis; import duckdb; con = ibis.duckdb.connect(); con_duckdb = con.con; sql_commands = '''{}'''; [con.raw_sql(cmd.strip()) for cmd in sql_commands.strip().split(';') if cmd.strip()]; metacon = ibis.sqlite.connect('{}'); ibis.options.interactive = True; ibis.options.repr.interactive.max_rows = 40; ibis.set_backend(con); 
try:
    import dkdc
    from dkdc import files, secrets
except ImportError:
    files = None; secrets = None; dkdc = None
namespace = {{'ibis': ibis, 'con': con, 'duckdb': duckdb, 'con_duckdb': con_duckdb, 'metacon': metacon}}
if dkdc:
    namespace.update({{'dkdc': dkdc, 'files': files, 'secrets': secrets}})
print('\nNamespace objects: con, con_duckdb, metacon, ibis, duckdb' + (', dkdc, files, secrets' if dkdc else ''))
print('Type "help(object)" for help on any object\n')"#,
            sql_commands,
            metadata_path.display()
        );

        // Launch IPython directly with the setup code
        let status = Command::new(python_path)
            .args(["-m", "IPython", "--no-banner", "-i", "-c", &setup_code])
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
