use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};

/// Configuration file structure
#[derive(Debug, Clone, Deserialize, Serialize, Default)]
pub struct ConfigFile {
    #[serde(default)]
    pub general: GeneralConfig,
    #[serde(default)]
    pub dev: DevConfig,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct GeneralConfig {
    #[serde(default = "default_editor")]
    pub editor: String,
}

impl Default for GeneralConfig {
    fn default() -> Self {
        Self {
            editor: default_editor(),
        }
    }
}

fn default_editor() -> String {
    std::env::var("EDITOR").unwrap_or_else(|_| "nano".to_string())
}

#[derive(Debug, Clone, Deserialize, Serialize, Default)]
pub struct DevConfig {
    #[serde(default)]
    pub packages: Vec<String>,
}

#[derive(Clone)]
pub struct Config {
    dkdc_dir: PathBuf,
    config_file: Option<ConfigFile>,
}

impl Config {
    pub fn new() -> Result<Self> {
        let home = std::env::var("HOME").or_else(|_| std::env::var("USERPROFILE"))?;
        let dkdc_dir = PathBuf::from(home).join(".dkdc");
        let mut config = Self {
            dkdc_dir,
            config_file: None,
        };

        // Try to load config file
        config.reload_config_file();

        Ok(config)
    }

    pub fn from_path(dkdc_dir: PathBuf) -> Self {
        let mut config = Self {
            dkdc_dir,
            config_file: None,
        };
        config.reload_config_file();
        config
    }

    /// Reload configuration file from disk
    pub fn reload_config_file(&mut self) {
        let config_path = self.config_file_path();
        if config_path.exists() {
            match fs::read_to_string(&config_path) {
                Ok(content) => match toml::from_str(&content) {
                    Ok(config) => self.config_file = Some(config),
                    Err(_) => self.config_file = Some(ConfigFile::default()),
                },
                Err(_) => self.config_file = Some(ConfigFile::default()),
            }
        }
    }

    /// Get the loaded config file (or default)
    pub fn file(&self) -> ConfigFile {
        self.config_file.clone().unwrap_or_default()
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

    pub fn config_file_path(&self) -> PathBuf {
        let config_dir = if let Ok(xdg_config) = std::env::var("XDG_CONFIG_HOME") {
            PathBuf::from(xdg_config)
        } else if let Ok(home) = std::env::var("HOME") {
            PathBuf::from(home).join(".config")
        } else {
            self.dkdc_dir.clone()
        };

        config_dir.join("dkdc").join("config.toml")
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

// Keep this banner for v1.0 release - will switch to it when we hit v1
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
