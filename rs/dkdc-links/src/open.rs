use anyhow::{Context, Result};
use std::sync::Arc;
use tokio::sync::Semaphore;

use crate::config::Config;

pub fn alias_or_link_to_uri(link: &str, config: &Config) -> Result<String> {
    // Check if it's an alias first
    if let Some(alias_target) = config.aliases.get(link) {
        // Now check if the alias target is in links
        if let Some(uri) = config.links.get(alias_target) {
            return Ok(uri.clone());
        }
    }

    // Check if it's directly in links
    if let Some(uri) = config.links.get(link) {
        return Ok(uri.clone());
    }

    anyhow::bail!("'{}' not found in [links] or [aliases]", link)
}

fn open_it(link: &str) -> Result<()> {
    open::that(link).with_context(|| format!("failed to open {}", link))?;
    println!("opening {}...", link);
    Ok(())
}

pub async fn open_links(
    links: Vec<String>,
    max_workers: usize,
    config: Arc<Config>,
) -> Result<()> {
    let num_cpus = num_cpus::get();
    let max_workers = if max_workers == 0 || max_workers > num_cpus {
        num_cpus
    } else {
        max_workers
    };

    let semaphore = Arc::new(Semaphore::new(max_workers));
    let mut handles = vec![];

    for link in links {
        let permit = semaphore.clone().acquire_owned().await?;
        let config = config.clone();

        let handle = tokio::spawn(async move {
            let _permit = permit;

            match alias_or_link_to_uri(&link, &config) {
                Ok(uri) => {
                    if let Err(e) = open_it(&uri) {
                        eprintln!("[dkdc] failed to open {}: {}", link, e);
                    }
                }
                Err(e) => {
                    eprintln!("[dkdc] skipping {}: {}", link, e);
                }
            }
        });

        handles.push(handle);
    }

    // Wait for all tasks to complete
    for handle in handles {
        handle.await?;
    }

    Ok(())
}
