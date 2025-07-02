use anyhow::Result;
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Clone)]
pub struct Config {
    dkdc_dir: PathBuf,
}

impl Config {
    pub fn new() -> Result<Self> {
        let home = std::env::var("HOME").or_else(|_| std::env::var("USERPROFILE"))?;
        let dkdc_dir = PathBuf::from(home).join(".dkdc");
        Ok(Self { dkdc_dir })
    }

    pub fn from_path(dkdc_dir: PathBuf) -> Self {
        Self { dkdc_dir }
    }

    pub fn dkdc_dir(&self) -> &Path {
        &self.dkdc_dir
    }

    pub fn lake_dir(&self) -> PathBuf {
        self.dkdc_dir.join("dkdclake")
    }

    pub fn metadata_path(&self) -> PathBuf {
        self.lake_dir().join("metadata.db")
    }

    pub fn data_path(&self) -> PathBuf {
        self.lake_dir().join("data")
    }

    pub fn venv_path(&self) -> PathBuf {
        self.dkdc_dir.join("venv")
    }

    pub fn python_path(&self) -> PathBuf {
        let venv = self.venv_path();
        if cfg!(windows) {
            venv.join("Scripts").join("python.exe")
        } else {
            venv.join("bin").join("python")
        }
    }

    pub fn ensure_directories(&self) -> Result<()> {
        fs::create_dir_all(&self.dkdc_dir)?;
        fs::create_dir_all(self.lake_dir())?;
        fs::create_dir_all(self.data_path())?;
        Ok(())
    }

    pub fn ensure_metadata_db(&self) -> Result<()> {
        self.ensure_directories()?;

        if !self.metadata_path().exists() {
            fs::File::create(self.metadata_path())?;
        }

        Ok(())
    }
}

pub const SECRETS_TABLE_NAME: &str = "secrets";
pub const FILES_TABLE_NAME: &str = "files";
pub const ARCHIVES_TABLE_NAME: &str = "archives";

pub const DUCKLAKE_EXTENSION: &str = "ducklake";
pub const SQLITE_EXTENSION: &str = "sqlite";

pub const ARCHIVE_FILENAME_TEMPLATE: &str = "archive_directory_{name}.zip";

pub struct Colors;

impl Colors {
    pub const PRIMARY: &'static str = "#8b5cf6";
    pub const SECONDARY: &'static str = "#06b6d4";
    pub const SUCCESS: &'static str = "#10b981";
    pub const WARNING: &'static str = "#f59e0b";
    pub const ERROR: &'static str = "#ef4444";
    pub const MUTED: &'static str = "#6b7280";
    pub const ACCENT: &'static str = "#a855f7";
}

pub const DKDC_BANNER: &str = r#"
▓█████▄  ██ ▄█▀▓█████▄  ▄████▄  
▒██▀ ██▌ ██▄█▒ ▒██▀ ██▌▒██▀ ▀█  
░██   █▌▓███▄░ ░██   █▌▒▓█    ▄ 
░▓█▄   ▌▓██ █▄ ░▓█▄   ▌▒▓▓▄ ▄██▒
░▒████▓ ▒██▒ █▄░▒████▓ ▒ ▓███▀ ░
 ▒▒▓  ▒ ▒ ▒▒ ▓▒ ▒▒▓  ▒ ░ ░▒ ▒  ░
 ░ ▒  ▒ ░ ░▒ ▒░ ░ ▒  ▒   ░  ▒   
 ░ ░  ░ ░ ░░ ░  ░ ░  ░ ░        
   ░    ░  ░      ░    ░ ░      
 ░              ░      ░

develop knowledge, develop code
"#;

#[allow(dead_code)]
pub const DKDC_BANNER_V1: &str = r#"
██████╗ ██╗  ██╗██████╗  ██████╗
██╔══██╗██║ ██╔╝██╔══██╗██╔════╝
██║  ██║█████╔╝ ██║  ██║██║     
██║  ██║██╔═██╗ ██║  ██║██║     
██████╔╝██║  ██╗██████╔╝╚██████╗
╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝

develop knowledge, develop code
"#;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_config_creation() {
        let config = Config::new();
        assert!(config.is_ok());
    }

    #[test]
    fn test_paths() {
        let config = Config::from_path(PathBuf::from("/home/test/.dkdc"));
        assert_eq!(config.dkdc_dir().display().to_string(), "/home/test/.dkdc");
        assert_eq!(
            config.lake_dir().display().to_string(),
            "/home/test/.dkdc/dkdclake"
        );
        assert_eq!(
            config.metadata_path().display().to_string(),
            "/home/test/.dkdc/dkdclake/metadata.db"
        );
    }
}
