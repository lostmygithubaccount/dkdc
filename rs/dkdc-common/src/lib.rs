/// Common utilities for dkdc
pub mod version;

use anyhow::Result;

/// Gitignore pattern handling
pub mod gitignore {
    use std::path::Path;

    /// Load gitignore patterns from a directory
    pub fn load_patterns(base_path: &Path) -> Vec<String> {
        let mut patterns = vec![
            // Always ignore .git
            ".git".to_string(),
            ".git/**".to_string(),
        ];

        // Load .gitignore if it exists
        let gitignore_path = base_path.join(".gitignore");
        if gitignore_path.exists() {
            if let Ok(content) = std::fs::read_to_string(&gitignore_path) {
                for line in content.lines() {
                    let line = line.trim();
                    if !line.is_empty() && !line.starts_with('#') {
                        patterns.push(line.to_string());
                    }
                }
            }
        }

        patterns
    }

    /// Check if a path should be ignored based on patterns
    pub fn should_ignore(path: &Path, patterns: &[String]) -> bool {
        let path_str = path.to_string_lossy();

        for pattern in patterns {
            // Simple pattern matching (not full gitignore syntax)
            if pattern.ends_with("/**") {
                let prefix = &pattern[..pattern.len() - 3];
                if path_str.starts_with(prefix) {
                    return true;
                }
            } else if pattern.contains('*') {
                if glob_match(pattern, &path_str) {
                    return true;
                }
            } else {
                // Exact match or prefix
                if &*path_str == pattern || path_str.starts_with(&format!("{}/", pattern)) {
                    return true;
                }
            }
        }

        false
    }

    /// Basic glob matching for * only
    fn glob_match(pattern: &str, text: &str) -> bool {
        let parts: Vec<&str> = pattern.split('*').collect();

        if parts.is_empty() {
            return false;
        }

        let mut pos = 0;
        for (i, part) in parts.iter().enumerate() {
            if i == 0 && !part.is_empty() {
                // Pattern doesn't start with *, must match beginning
                if !text.starts_with(part) {
                    return false;
                }
                pos = part.len();
            } else if i == parts.len() - 1 && !part.is_empty() {
                // Pattern doesn't end with *, must match end
                if !text[pos..].ends_with(part) {
                    return false;
                }
            } else if !part.is_empty() {
                // Find the part in the remaining text
                if let Some(idx) = text[pos..].find(part) {
                    pos += idx + part.len();
                } else {
                    return false;
                }
            }
        }

        true
    }
}

/// Format byte sizes for human readability
pub fn format_size(bytes: usize) -> String {
    const UNITS: &[&str] = &["B", "KB", "MB", "GB", "TB"];
    let mut size = bytes as f64;
    let mut unit_index = 0;

    while size >= 1024.0 && unit_index < UNITS.len() - 1 {
        size /= 1024.0;
        unit_index += 1;
    }

    if unit_index == 0 {
        format!("{} {}", size as usize, UNITS[unit_index])
    } else {
        format!("{:.1} {}", size, UNITS[unit_index])
    }
}

/// Validate paths and names
pub fn validate_name(name: &str) -> Result<()> {
    if name.is_empty() {
        anyhow::bail!("Name cannot be empty");
    }

    // Disallow path separators in names
    if name.contains('/') || name.contains('\\') {
        anyhow::bail!("Name cannot contain path separators");
    }

    // Disallow special characters that could cause issues
    if name.contains('\0') {
        anyhow::bail!("Name cannot contain null characters");
    }

    Ok(())
}
