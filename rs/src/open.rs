use anyhow::{Context, Result};
use std::sync::Arc;
use tokio::sync::Semaphore;

use crate::config::Config;

pub fn alias_or_thing_to_uri(thing: &str, config: &Config) -> Result<String> {
    // Check if it's an alias first
    if let Some(alias_target) = config.aliases.get(thing) {
        // Now check if the alias target is in things
        if let Some(uri) = config.things.get(alias_target) {
            return Ok(uri.clone());
        }
    }

    // Check if it's directly in things
    if let Some(uri) = config.things.get(thing) {
        return Ok(uri.clone());
    }

    anyhow::bail!("'{}' not found in [things] or [aliases]", thing)
}

fn open_it(thing: &str) -> Result<()> {
    open::that(thing).with_context(|| format!("failed to open {}", thing))?;
    println!("opening {}...", thing);
    Ok(())
}

pub async fn open_things(
    things: Vec<String>,
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

    for thing in things {
        let permit = semaphore.clone().acquire_owned().await?;
        let config = config.clone();

        let handle = tokio::spawn(async move {
            let _permit = permit;

            match alias_or_thing_to_uri(&thing, &config) {
                Ok(uri) => {
                    if let Err(e) = open_it(&uri) {
                        eprintln!("[dkdc] failed to open {}: {}", thing, e);
                    }
                }
                Err(e) => {
                    eprintln!("[dkdc] skipping {}: {}", thing, e);
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
