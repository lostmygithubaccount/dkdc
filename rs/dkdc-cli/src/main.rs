use anyhow::Result;
use clap::{Parser, Subcommand};
use dkdc_dev::{Dev, DevMode};
use dkdc_lake::Lake;

#[derive(Parser)]
#[command(name = "dkdc")]
#[command(about = "dkdc: don't know, don't care", long_about = None)]
#[command(version)]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,
    
    /// Open config file in editor
    #[arg(short, long)]
    config: bool,
}

#[derive(Subcommand)]
enum Commands {
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
        path: String,
        
        /// Name for the archive
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
enum FilesCommands {
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
enum SecretsCommands {
    /// Set a secret
    Set {
        /// Secret name
        name: String,
        
        /// Secret value (will prompt if not provided)
        #[arg(short, long)]
        value: Option<String>,
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
    
    /// Export secrets as .env file
    Export {
        /// Output file path
        #[arg(default_value = ".env")]
        output: String,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    
    if cli.config {
        println!("Config editing not yet implemented in Rust version");
        return Ok(());
    }
    
    if cli.command.is_none() {
        use clap::CommandFactory;
        Cli::command().print_help()?;
        return Ok(());
    }
    
    match cli.command {
        Some(Commands::Dev { sql, exit }) => {
            let dev = Dev::new()?;
            
            if exit {
                println!("Setup complete");
                return Ok(());
            }
            
            let mode = if sql { DevMode::Sql } else { DevMode::Python };
            dev.launch(mode)?;
        }
        
        Some(Commands::Archive { path: _, name: _ }) => {
            println!("Archive command not yet implemented");
        }
        
        Some(Commands::Files { command }) => {
            handle_files_command(command)?;
        }
        
        Some(Commands::Secrets { command }) => {
            match command {
                SecretsCommands::List => {
                    let lake = Lake::new()?;
                    let secrets = lake.list_secrets()?;
                    for secret in secrets {
                        println!("{}", secret);
                    }
                }
                _ => println!("Secrets subcommand not yet implemented"),
            }
        }
        
        Some(Commands::Backup) => {
            println!("Backup command not yet implemented");
        }
        
        None => unreachable!("Clap should handle this case")
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