use anyhow::Result;
use clap::{Parser, Subcommand};
use dkdc_config::Config;
use dkdc_dev::{Dev, DevMode};
use dkdc_lake::Lake;
use std::process::Command;

#[derive(Parser)]
#[command(name = "dkdc")]
#[command(about = "dkdc: don't know, don't care", long_about = None)]
#[command(version)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Option<Commands>,

    /// Open config file in editor
    #[arg(short, long)]
    pub config: bool,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Enter a development REPL (IPython or DuckDB)
    Dev {
        /// Enter DuckDB CLI instead of IPython
        #[arg(long)]
        sql: bool,

        /// Exit after setup without starting REPL
        #[arg(long)]
        exit: bool,
    },

    /// Archive a directory to the datalake
    Archive {
        /// Path to directory to archive
        #[arg(default_value = ".")]
        path: String,

        /// Name for the archive (defaults to directory name.zip)
        #[arg(short, long)]
        name: Option<String>,
    },

    /// Work with files in the virtual filesystem
    Files {
        #[command(subcommand)]
        command: FilesCommands,
    },

    /// Manage secrets
    Secrets {
        #[command(subcommand)]
        command: SecretsCommands,
    },

    /// Backup management (future)
    Backup,
}

#[derive(Subcommand)]
pub enum FilesCommands {
    /// List files
    List {
        /// Directory path (default: ./files)
        #[arg(default_value = "./files")]
        path: String,
    },

    /// Add a file
    Add {
        /// Local file path
        file: String,

        /// Virtual path in filesystem
        #[arg(short, long)]
        path: Option<String>,
    },

    /// Open a file
    Open {
        /// File name
        name: String,

        /// Directory path
        #[arg(short, long, default_value = "./files")]
        path: String,
    },

    /// Dump files to local directory
    Dump {
        /// Local directory to dump to
        #[arg(default_value = ".")]
        output: String,
    },

    /// Restore files from local directory
    Restore {
        /// Local directory to restore from
        directory: String,
    },
}

#[derive(Subcommand)]
pub enum SecretsCommands {
    /// Set a secret
    Set {
        /// Secret name
        name: String,

        /// Secret value (will prompt if not provided)
        #[arg(short, long)]
        value: Option<String>,

        /// Force overwrite existing secret
        #[arg(short, long)]
        force: bool,

        /// Read value from stdin
        #[arg(long)]
        stdin: bool,
    },

    /// Get a secret
    Get {
        /// Secret name
        name: String,

        /// Copy to clipboard
        #[arg(short, long)]
        clipboard: bool,
    },

    /// List all secrets
    List,

    /// Delete a secret
    Delete {
        /// Secret name
        name: String,
    },

    /// Export secrets in various formats
    Export {
        /// Output file path (use - for stdout)
        #[arg(default_value = "-")]
        output: String,

        /// Export format: shell, dotenv, json
        #[arg(short, long, default_value = "shell")]
        format: String,

        /// Only export secrets with this prefix
        #[arg(short, long)]
        prefix: Option<String>,
    },
}

/// Run the CLI with the given arguments
pub fn run_cli(args: Vec<String>) -> Result<()> {
    let cli = Cli::parse_from(args);

    if cli.config {
        return handle_config_edit();
    }

    if cli.command.is_none() {
        use clap::CommandFactory;
        Cli::command().print_help()?;
        return Ok(());
    }

    match cli.command {
        Some(Commands::Dev { sql, exit }) => {
            let dev = Dev::new()?;
            let mode = if sql { DevMode::Sql } else { DevMode::Python };

            if exit {
                // For Python mode, ensure environment is set up even with --exit
                if let DevMode::Python = mode {
                    dev.ensure_python_env()?;
                }
                println!("Setup complete");
                return Ok(());
            }

            dev.launch(mode)?;
        }

        Some(Commands::Archive { path, name }) => {
            dkdc_archive::archive_directory(&path, name.as_deref())?;
        }

        Some(Commands::Files { command }) => {
            handle_files_command(command)?;
        }

        Some(Commands::Secrets { command }) => {
            handle_secrets_command(command)?;
        }

        Some(Commands::Backup) => {
            println!("Backup command not yet implemented");
        }

        None => unreachable!("Clap should handle this case"),
    }

    Ok(())
}

fn handle_files_command(command: FilesCommands) -> Result<()> {
    match command {
        FilesCommands::List { path } => dkdc_files::list_files(&path),
        FilesCommands::Add { file, path } => dkdc_files::add_file(&file, path.as_deref()),
        FilesCommands::Open { name, path } => dkdc_files::open_file(&name, &path),
        FilesCommands::Dump { output } => dkdc_files::dump_files(&output),
        FilesCommands::Restore { directory } => dkdc_files::restore_files(&directory),
    }
}

fn handle_config_edit() -> Result<()> {
    let config = Config::new()?;
    let config_path = config.config_file_path();

    // Ensure config directory exists
    if let Some(parent) = config_path.parent() {
        std::fs::create_dir_all(parent)?;
    }

    // Create default config if it doesn't exist
    if !config_path.exists() {
        let default_config = r#"# dkdc configuration file

[general]
# Default editor for opening files
editor = "nano"

[dev]
# Additional Python packages to install in dev environment
# packages = ["pandas", "matplotlib"]
"#;
        std::fs::write(&config_path, default_config)?;
    }

    // Get editor from config file or environment
    let editor = config.file().general.editor;

    // Basic validation to prevent command injection
    if editor.contains(';') || editor.contains('&') || editor.contains('|') || editor.contains('`')
    {
        eprintln!("Error: Invalid editor command");
        std::process::exit(1);
    }

    // Open config in editor
    let status = Command::new(&editor).arg(&config_path).status()?;

    if !status.success() {
        eprintln!("Editor exited with error");
        std::process::exit(1);
    }

    Ok(())
}

fn handle_secrets_command(command: SecretsCommands) -> Result<()> {
    match command {
        SecretsCommands::List => {
            let lake = Lake::new()?;
            let secrets = lake.list_secrets()?;
            for secret in secrets {
                println!("{}", secret);
            }
            Ok(())
        }
        SecretsCommands::Set {
            name,
            value,
            force,
            stdin,
        } => {
            use rpassword::read_password;
            use std::io::{self, Read, Write};

            let lake = Lake::new()?;

            // Check if secret exists and force flag
            if !force && lake.get_secret(&name)?.is_some() {
                eprintln!("Error: Secret '{}' already exists", name);
                eprintln!("Use --force to overwrite");
                std::process::exit(1);
            }

            let secret_value = if stdin {
                if value.is_some() {
                    eprintln!("Error: Cannot specify both value and --stdin");
                    std::process::exit(1);
                }
                let mut buffer = String::new();
                io::stdin().read_to_string(&mut buffer)?;
                buffer.trim().to_string()
            } else if let Some(val) = value {
                val
            } else {
                print!("Enter value: ");
                io::stdout().flush()?;
                let val = read_password()?;

                print!("Confirm value: ");
                io::stdout().flush()?;
                let confirm = read_password()?;

                if val != confirm {
                    eprintln!("Values don't match");
                    std::process::exit(1);
                }

                val
            };

            if secret_value.is_empty() {
                eprintln!("Error: Secret value cannot be empty");
                std::process::exit(1);
            }

            lake.set_secret(&name, secret_value.as_bytes())?;
            eprintln!("✓ Secret '{}' saved", name);
            Ok(())
        }
        SecretsCommands::Get { name, clipboard } => {
            let lake = Lake::new()?;

            if let Some(secret_data) = lake.get_secret(&name)? {
                let secret_value = String::from_utf8_lossy(&secret_data);

                if clipboard {
                    use clipboard::{ClipboardContext, ClipboardProvider};
                    let mut ctx: ClipboardContext = ClipboardProvider::new().unwrap();
                    ctx.set_contents(secret_value.to_string()).unwrap();
                    eprintln!("Copied to clipboard");
                } else {
                    use std::io::Write;
                    print!("{}", secret_value);
                    std::io::stdout().flush()?;
                }
            } else {
                eprintln!("Error: Secret '{}' not found", name);
                std::process::exit(1);
            }

            Ok(())
        }
        SecretsCommands::Delete { name } => {
            let lake = Lake::new()?;

            if lake.delete_secret(&name)? {
                eprintln!("✓ Secret '{}' deleted", name);
            } else {
                eprintln!("Error: Secret '{}' not found", name);
                std::process::exit(1);
            }

            Ok(())
        }
        SecretsCommands::Export {
            output,
            format,
            prefix,
        } => {
            let lake = Lake::new()?;
            let mut secrets = lake.list_secrets()?;

            // Filter by prefix if provided
            if let Some(p) = &prefix {
                secrets.retain(|s| s.starts_with(p));
            }

            if secrets.is_empty() {
                eprintln!(
                    "# No secrets found{}",
                    if prefix.is_some() {
                        format!(" with prefix '{}'", prefix.unwrap())
                    } else {
                        String::new()
                    }
                );
                return Ok(());
            }

            // Collect secrets data
            let mut secret_map = std::collections::HashMap::new();
            for name in &secrets {
                if let Some(data) = lake.get_secret(name)? {
                    secret_map.insert(name.clone(), String::from_utf8_lossy(&data).to_string());
                }
            }

            // Format output
            let formatted_output = match format.as_str() {
                "shell" => {
                    let mut out = String::from("# dkdc secrets export\n");
                    for (name, value) in &secret_map {
                        let escaped = value.replace("'", "'\"'\"'");
                        out.push_str(&format!("export {}='{}'\n", name, escaped));
                    }
                    out
                }
                "dotenv" => {
                    let mut out = String::from("# dkdc secrets export\n");
                    for (name, value) in &secret_map {
                        let escaped = value.replace('"', r#"\""#).replace('\n', r"\n");
                        out.push_str(&format!(
                            r#"{}="{}"
"#,
                            name, escaped
                        ));
                    }
                    out
                }
                "json" => serde_json::to_string_pretty(&secret_map)?,
                _ => {
                    eprintln!("Error: Unknown format '{}'", format);
                    std::process::exit(1);
                }
            };

            // Write to output
            if output == "-" {
                print!("{}", formatted_output);
            } else {
                std::fs::write(&output, formatted_output)?;
                eprintln!("✓ Exported to {}", output);
            }

            Ok(())
        }
    }
}
