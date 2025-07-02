use anyhow::Result;
use clap::{Parser, Subcommand};
use dkdc_files::{list_files, add_file, open_file, dump_files, restore_files};

#[derive(Parser)]
#[command(name = "dkdc-files")]
#[command(about = "Manage files in the virtual filesystem", long_about = None)]
#[command(version)]
#[command(arg_required_else_help = true)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
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

fn main() -> Result<()> {
    let cli = Cli::parse();
    
    match cli.command {
        Commands::List { path } => list_files(&path),
        Commands::Add { file, path } => add_file(&file, path.as_deref()),
        Commands::Open { name, path } => open_file(&name, &path),
        Commands::Dump { output } => dump_files(&output),
        Commands::Restore { directory } => restore_files(&directory),
    }
}