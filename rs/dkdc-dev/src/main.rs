use anyhow::Result;
use clap::Parser;
use dkdc_dev::{Dev, DevMode};

#[derive(Parser)]
#[command(name = "dkdc-dev")]
#[command(about = "Development REPL for dkdc", long_about = None)]
#[command(version)]
struct Cli {
    /// Enter DuckDB CLI instead of IPython
    #[arg(long)]
    sql: bool,
    
    /// Exit after setup without starting REPL
    #[arg(long)]
    exit: bool,
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    
    let dev = Dev::new()?;
    
    if cli.exit {
        println!("Setup complete");
        return Ok(());
    }
    
    let mode = if cli.sql { DevMode::Sql } else { DevMode::Python };
    dev.launch(mode)?;
    
    Ok(())
}