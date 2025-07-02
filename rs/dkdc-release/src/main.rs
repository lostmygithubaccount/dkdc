use anyhow::Result;
use clap::{Parser, Subcommand};
use std::process::Command;

#[derive(Parser)]
#[command(name = "dkdc-release")]
#[command(about = "Release automation for dkdc")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Check if ready for release
    Check,
    /// Build release artifacts
    Build,
    /// Publish to PyPI and crates.io
    Publish {
        /// Only publish Python package
        #[arg(long)]
        python_only: bool,
        /// Only publish Rust crates
        #[arg(long)]
        rust_only: bool,
        /// Dry run (don't actually publish)
        #[arg(long)]
        dry_run: bool,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Check => check_release()?,
        Commands::Build => build_release()?,
        Commands::Publish {
            python_only,
            rust_only,
            dry_run,
        } => publish_release(python_only, rust_only, dry_run)?,
    }

    Ok(())
}

fn check_release() -> Result<()> {
    println!("🔍 Checking release readiness...\n");

    // Check git status
    println!("📋 Checking git status...");
    let output = Command::new("git")
        .args(["status", "--porcelain"])
        .output()?;

    if !output.stdout.is_empty() {
        println!("❌ Working directory has uncommitted changes");
        return Ok(());
    }
    println!("✅ Working directory clean");

    // Check if on main branch
    let branch = Command::new("git")
        .args(["rev-parse", "--abbrev-ref", "HEAD"])
        .output()?;
    let branch = String::from_utf8_lossy(&branch.stdout).trim().to_string();

    if branch != "main" {
        println!("⚠️  Not on main branch (current: {})", branch);
    } else {
        println!("✅ On main branch");
    }

    // Run tests
    println!("\n📋 Running tests...");
    let status = Command::new("./bin/test.sh").status()?;
    if !status.success() {
        println!("❌ Tests failed");
        return Ok(());
    }
    println!("✅ Tests passed");

    // Check formatting
    println!("\n📋 Checking code formatting...");
    let status = Command::new("./bin/check.sh").status()?;
    if !status.success() {
        println!("❌ Code formatting issues");
        return Ok(());
    }
    println!("✅ Code formatting good");

    println!("\n🎉 Ready for release!");
    Ok(())
}

fn build_release() -> Result<()> {
    println!("🔨 Building release artifacts...\n");

    // Clean previous builds
    println!("🧹 Cleaning previous builds...");
    Command::new("rm")
        .args(["-rf", "dist/", "target/wheels/"])
        .status()?;

    // Build Python wheel
    println!("\n🐍 Building Python wheel...");
    let status = Command::new("uv")
        .args(["run", "maturin", "build", "--release"])
        .status()?;

    if !status.success() {
        println!("❌ Python build failed");
        return Ok(());
    }

    // Copy wheels to standard location
    std::fs::create_dir_all("target/wheels")?;

    // Find wheels in maturin's output directory
    if let Ok(entries) = std::fs::read_dir("rs/dkdc-py/target/wheels") {
        for entry in entries.filter_map(|e| e.ok()) {
            if entry
                .path()
                .extension()
                .map(|ext| ext == "whl")
                .unwrap_or(false)
            {
                let dest = std::path::Path::new("target/wheels").join(entry.file_name());
                std::fs::copy(entry.path(), dest)?;
            }
        }
    }

    // List artifacts
    println!("\n📦 Built artifacts:");
    Command::new("ls")
        .args(["-la", "target/wheels/"])
        .status()?;

    println!("\n✅ Build complete!");
    Ok(())
}

fn publish_release(python_only: bool, rust_only: bool, dry_run: bool) -> Result<()> {
    if dry_run {
        println!("🏃 DRY RUN - No packages will be published\n");
    }

    if !rust_only {
        println!("📦 Publishing Python package to PyPI...");

        if dry_run {
            println!("  Would run: uv publish");
        } else {
            // Get list of wheel files
            let wheels = std::fs::read_dir("target/wheels")?
                .filter_map(|entry| entry.ok())
                .filter(|entry| {
                    entry
                        .path()
                        .extension()
                        .and_then(|ext| ext.to_str())
                        .map(|ext| ext == "whl")
                        .unwrap_or(false)
                })
                .collect::<Vec<_>>();

            if wheels.is_empty() {
                println!("❌ No wheel files found in target/wheels/");
                return Ok(());
            }

            for wheel in wheels {
                println!("  Publishing {}...", wheel.file_name().to_string_lossy());
                let status = Command::new("uv")
                    .env(
                        "UV_PUBLISH_TOKEN",
                        std::env::var("PYPI_TOKEN").unwrap_or_default(),
                    )
                    .args(["publish", wheel.path().to_str().unwrap()])
                    .status()?;

                if !status.success() {
                    println!("❌ Python publish failed");
                    return Ok(());
                }
            }

            println!("✅ Python package published!");
        }
    }

    if !python_only {
        println!("\n📦 Publishing Rust crates to crates.io...");

        let crates = [
            "dkdc-common",
            "dkdc-lake",
            "dkdc-files",
            "dkdc-secrets",
            "dkdc-archive",
            "dkdc-dev",
            "dkdc-cli",
            "dkdc-links",
        ];

        for crate_name in &crates {
            println!("\n  Publishing {}...", crate_name);

            if dry_run {
                println!("  Would run: cargo publish -p {}", crate_name);
            } else {
                let status = Command::new("cargo")
                    .current_dir("rs")
                    .args(["publish", "-p", crate_name])
                    .status()?;

                if !status.success() {
                    println!("❌ Failed to publish {}", crate_name);
                    println!(
                        "   You may need to wait for dependencies to be available on crates.io"
                    );
                    return Ok(());
                }

                // Wait a bit between publishes to ensure crates.io has processed
                std::thread::sleep(std::time::Duration::from_secs(5));
            }
        }

        println!("\n✅ All Rust crates published!");
    }

    Ok(())
}
