//! Secrets management for dkdc
//!
//! This module provides a simple interface for managing encrypted secrets
//! stored in the dkdc data lake.

use anyhow::Result;
use dkdc_lake::Lake;

/// List all secret names
pub fn list_secrets() -> Result<Vec<String>> {
    let lake = Lake::new()?;
    lake.list_secrets()
}

/// Set a secret value
pub fn set_secret(name: &str, value: &[u8]) -> Result<()> {
    let lake = Lake::new()?;
    lake.set_secret(name, value)
}

/// Get a secret value
pub fn get_secret(name: &str) -> Result<Option<Vec<u8>>> {
    let lake = Lake::new()?;
    lake.get_secret(name)
}

/// Delete a secret
pub fn delete_secret(name: &str) -> Result<()> {
    let lake = Lake::new()?;
    lake.delete_secret(name)?;
    Ok(())
}
