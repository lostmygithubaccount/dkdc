use anyhow::Result;
use clap::Parser;
use std::sync::Arc;

use dkdc_links::config::{config_it, init_config, load_config, print_config};
use dkdc_links::open::open_links;

#[derive(Parser, Debug)]
#[command(name = "dkdc-links")]
#[command(about = "bookmarks in your terminal")]
#[command(version)]
struct Args {
    /// Configure dkdc
    #[arg(short, long)]
    config: bool,

    /// Maximum number of workers for parallel processing (0 = use all CPUs)
    #[arg(short, long, default_value = "1")]
    max_workers: usize,

    /// Things to open
    links: Vec<String>,
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = Args::parse();

    // Initialize config (creates default if doesn't exist)
    init_config()?;

    // Handle --config flag
    if args.config {
        config_it()?;
        return Ok(());
    }

    // Load config
    let config = Arc::new(load_config()?);

    // If no arguments, print config
    if args.links.is_empty() {
        print_config(&config)?;
    } else {
        // Open the links
        open_links(args.links, args.max_workers, config).await?;
    }

    Ok(())
}
