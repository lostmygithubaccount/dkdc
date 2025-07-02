use anyhow::Result;
use clap::Parser;

#[derive(Parser)]
#[command(name = "dkdc-archive")]
#[command(about = "Archive directories to dkdc", long_about = None)]
#[command(version)]
struct Cli {
    /// Path to directory to archive
    #[arg(default_value = ".")]
    path: String,

    /// Name for the archive
    #[arg(short, long)]
    name: Option<String>,
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    if let Err(e) = dkdc_archive::archive_directory(&cli.path, cli.name.as_deref()) {
        eprintln!("Error: {}", e);
        std::process::exit(1);
    }

    Ok(())
}
