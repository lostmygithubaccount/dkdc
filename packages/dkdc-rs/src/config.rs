use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;

#[derive(Debug, Serialize, Deserialize, Default)]
pub struct Config {
    #[serde(default)]
    pub aliases: HashMap<String, String>,
    #[serde(default)]
    pub things: HashMap<String, String>,
}

const DEFAULT_CONFIG: &str = r#"# dkdc config file
[aliases]
a = "thing"
alias = "thing"
[things]
thing = "https://github.com/lostmygithubaccount/dkdc"
"#;

pub fn config_path() -> Result<PathBuf> {
    let home_dir = dirs::home_dir().context("Failed to get home directory")?;
    Ok(home_dir.join(".dkdc").join("config.toml"))
}

pub fn init_config() -> Result<()> {
    let config_path = config_path()?;
    let config_dir = config_path.parent().unwrap();

    fs::create_dir_all(config_dir).context("Failed to create config directory")?;

    if !config_path.exists() {
        fs::write(&config_path, DEFAULT_CONFIG).context("Failed to write default config")?;
    }

    Ok(())
}

pub fn load_config() -> Result<Config> {
    let config_path = config_path()?;
    let contents = fs::read_to_string(&config_path).context("Failed to read config file")?;
    let config: Config = toml::from_str(&contents).context("Failed to parse config file")?;
    Ok(config)
}

pub fn config_it() -> Result<()> {
    let config_path = config_path()?;
    let editor = std::env::var("EDITOR").unwrap_or_else(|_| "vi".to_string());

    println!("opening {} with {}...", config_path.display(), editor);

    let status = std::process::Command::new(&editor)
        .arg(&config_path)
        .status()
        .with_context(|| format!("editor {} not found in PATH", editor))?;

    if !status.success() {
        anyhow::bail!("Editor exited with non-zero status");
    }

    Ok(())
}

pub fn print_config(config: &Config) -> Result<()> {
    let sections = vec![("aliases", &config.aliases), ("things", &config.things)];

    for (section_name, section_data) in sections {
        if section_data.is_empty() {
            continue;
        }

        println!("{}:", section_name);
        println!();

        let mut keys: Vec<_> = section_data.keys().collect();
        keys.sort();

        let max_key_len = keys.iter().map(|k| k.len()).max().unwrap_or(0);

        for key in keys {
            if let Some(value) = section_data.get(key) {
                println!("• {:<width$} | {}", key, value, width = max_key_len);
            }
        }

        println!();
    }

    Ok(())
}
