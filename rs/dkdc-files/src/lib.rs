use anyhow::Result;
use dkdc_lake::Lake;
use std::fs;
use std::path::Path;

pub fn list_files(path: &str) -> Result<()> {
    let lake = Lake::new()?;
    let files = lake.list_files(path)?;

    for file in files {
        println!("{}", file);
    }

    Ok(())
}

pub fn add_file(file: &str, path: Option<&str>) -> Result<()> {
    let file_path = Path::new(file);

    if !file_path.exists() {
        anyhow::bail!("File not found: '{}'", file);
    }

    if !file_path.is_file() {
        anyhow::bail!("'{}' is not a file", file);
    }

    let filename = file_path
        .file_name()
        .and_then(|n| n.to_str())
        .ok_or_else(|| anyhow::anyhow!("Invalid filename"))?;

    let data = fs::read(file_path)?;
    let lake = Lake::new()?;
    let filepath = path.unwrap_or("./files");

    lake.add_file(filepath, filename, &data)?;

    // Just output the filename that was added, Unix style
    println!("{}", filename);

    Ok(())
}

pub fn open_file(name: &str, path: &str) -> Result<()> {
    use tempfile::Builder;

    let editor = std::env::var("EDITOR").unwrap_or_else(|_| "vim".to_string());
    let lake = Lake::new()?;

    // Get existing file content if it exists
    let existing_content = lake.get_file(path, name)?;
    let initial_content = existing_content
        .as_ref()
        .map(|f| f.filedata.as_slice())
        .unwrap_or(b"");

    // Extract file extension from name
    let extension = Path::new(name)
        .extension()
        .and_then(|ext| ext.to_str())
        .map(|ext| format!(".{}", ext))
        .unwrap_or_default();

    // Create temporary file with same extension for syntax highlighting
    let mut temp_file = Builder::new()
        .prefix("dkdc_")
        .suffix(&extension)
        .tempfile()?;

    use std::io::Write;
    temp_file.write_all(initial_content)?;

    // Get the path before we lose ownership
    let temp_path = temp_file.path().to_owned();

    // Keep the file alive while editing
    let _temp_file = temp_file.persist(&temp_path)?;

    // Open in editor
    let status = std::process::Command::new(&editor)
        .arg(&temp_path)
        .status()?;

    if !status.success() {
        anyhow::bail!("Editor exited with error");
    }

    // Read the edited content
    let final_content = fs::read(&temp_path)?;

    // Save if new file and not empty, or if existing file was changed
    if (existing_content.is_none() && !final_content.is_empty())
        || (existing_content.is_some() && final_content != initial_content)
    {
        lake.add_file(path, name, &final_content)?;
    }

    // Clean up the temporary file
    fs::remove_file(temp_path)?;

    Ok(())
}

pub fn dump_files(output: &str) -> Result<()> {
    let output_path = Path::new(output);
    fs::create_dir_all(output_path)?;

    let lake = Lake::new()?;
    let files = lake.list_files("./files")?;

    for filename in &files {
        if let Some(file) = lake.get_file("./files", filename)? {
            let file_path = output_path.join(filename);
            fs::write(&file_path, &file.filedata)?;
            // Output each file as it's dumped
            println!("{}", file_path.display());
        }
    }

    Ok(())
}

pub fn restore_files(directory: &str) -> Result<()> {
    let restore_path = Path::new(directory);

    if !restore_path.exists() {
        anyhow::bail!("Directory not found: {}", directory);
    }

    if !restore_path.is_dir() {
        anyhow::bail!("Not a directory: {}", directory);
    }

    let lake = Lake::new()?;

    for entry in fs::read_dir(restore_path)? {
        let entry = entry?;
        let path = entry.path();

        if path.is_file() {
            if let Some(filename) = path.file_name().and_then(|n| n.to_str()) {
                let data = fs::read(&path)?;
                lake.add_file("./files", filename, &data)?;
                // Output each file as it's restored
                println!("{}", filename);
            }
        }
    }

    Ok(())
}
