use anyhow::Result;
use dkdc_common::gitignore;
use dkdc_lake::Lake;
use std::fs;
use std::io::{Cursor, Write};
use std::path::Path;
use walkdir::WalkDir;
use zip::write::{FileOptions, ZipWriter};
use zip::CompressionMethod;

pub fn archive_directory(path: &str, name: Option<&str>) -> Result<()> {
    let dir_path = Path::new(path);
    if !dir_path.exists() {
        anyhow::bail!("'{}' does not exist", path);
    }

    if !dir_path.is_dir() {
        anyhow::bail!("'{}' is not a directory", path);
    }

    // Create archive name
    let archive_name = if let Some(n) = name {
        n.to_string()
    } else {
        let dir_name = dir_path
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("archive");
        format!("{}.zip", dir_name)
    };

    // Create zip in memory
    let mut buffer = Cursor::new(Vec::new());
    {
        let mut zip = ZipWriter::new(&mut buffer);
        let options: FileOptions<'_, ()> =
            FileOptions::default().compression_method(CompressionMethod::Deflated);

        // Load gitignore patterns
        let gitignore_patterns = gitignore::load_patterns(dir_path);

        // Walk directory and add files
        for entry in WalkDir::new(dir_path) {
            let entry = entry?;
            let path = entry.path();
            let relative_path = path.strip_prefix(dir_path)?;

            // Skip if matches gitignore
            if gitignore::should_ignore(relative_path, &gitignore_patterns) {
                continue;
            }

            if path.is_file() {
                let file_data = fs::read(path)?;
                zip.start_file(relative_path.to_string_lossy(), options)?;
                zip.write_all(&file_data)?;
            }
        }

        zip.finish()?;
    }

    // Get the zip data
    let zip_data = buffer.into_inner();

    // Store in lake
    let lake = Lake::new()?;
    lake.add_archive(&archive_name, &zip_data)?;

    eprintln!("✓ Archived '{}' as '{}'", path, archive_name);
    eprintln!("  Size: {}", dkdc_common::format_size(zip_data.len()));

    Ok(())
}
