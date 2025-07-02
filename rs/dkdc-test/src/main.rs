use anyhow::{Context, Result};
use clap::{Parser, Subcommand};
use colored::*;
use std::process::{Command, Stdio};
use tempfile::TempDir;

#[derive(Parser)]
#[command(name = "dkdc-test")]
#[command(about = "Test runner for dkdc")]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,

    /// Verbose output
    #[arg(short, long)]
    verbose: bool,
}

#[derive(Subcommand)]
enum Commands {
    /// Run all tests (default)
    All,
    /// Run only Rust tests
    Rust,
    /// Run only Python tests
    Python,
    /// Run only Go tests
    Go,
    /// Run only end-to-end tests
    E2e,
}

struct TestResult {
    name: String,
    passed: bool,
    output: Option<String>,
    skipped: bool,
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    let command = cli.command.unwrap_or(Commands::All);

    println!("{}", "🧪 Running tests...".bold());
    println!();

    let mut results = Vec::new();
    let verbose = cli.verbose;

    match command {
        Commands::All => {
            results.extend(run_rust_tests(verbose)?);
            results.extend(run_python_tests(verbose)?);
            results.extend(run_go_tests(verbose)?);
            results.extend(run_e2e_tests(verbose)?);
        }
        Commands::Rust => results.extend(run_rust_tests(verbose)?),
        Commands::Python => results.extend(run_python_tests(verbose)?),
        Commands::Go => results.extend(run_go_tests(verbose)?),
        Commands::E2e => results.extend(run_e2e_tests(verbose)?),
    }

    // Print summary
    println!();
    println!("{}", "━".repeat(50).dimmed());

    let total = results.len();
    let passed = results.iter().filter(|r| r.passed).count();
    let failed = results.iter().filter(|r| !r.passed && !r.skipped).count();
    let skipped = results.iter().filter(|r| r.skipped).count();

    if failed == 0 {
        if skipped > 0 {
            println!(
                "{} {} tests passed, {} skipped",
                "✅".bold(),
                passed.to_string().green().bold(),
                skipped.to_string().yellow()
            );
        } else {
            println!(
                "{} All {} tests passed!",
                "🎉".bold(),
                total.to_string().green().bold()
            );
        }
    } else {
        println!(
            "{} {} passed, {} failed, {} skipped",
            "❌".bold(),
            passed.to_string().green(),
            failed.to_string().red().bold(),
            skipped.to_string().yellow()
        );
        println!();
        println!("{}", "Failed tests:".red().bold());
        for result in &results {
            if !result.passed && !result.skipped {
                println!("  - {}", result.name.red());
                if let Some(output) = &result.output {
                    if verbose {
                        for line in output.lines().take(10) {
                            println!("    {}", line.dimmed());
                        }
                        if output.lines().count() > 10 {
                            println!("    {}", "... (truncated)".dimmed());
                        }
                    }
                }
            }
        }
        std::process::exit(1);
    }

    Ok(())
}

fn run_rust_tests(verbose: bool) -> Result<Vec<TestResult>> {
    println!("{} {}", "🦀".bold(), "Running Rust tests...".cyan());

    let mut results = Vec::new();

    // Run cargo test
    let output = Command::new("cargo")
        .current_dir("rs")
        .args(["test", "--workspace", "--quiet"])
        .output()
        .context("Failed to run cargo test")?;

    let passed = output.status.success();

    if passed {
        println!("  {} Rust tests", "✓".green());
    } else {
        println!("  {} Rust tests", "✗".red());
        if verbose {
            let stderr = String::from_utf8_lossy(&output.stderr);
            println!("{}", stderr.dimmed());
        }
    }

    results.push(TestResult {
        name: "Rust tests".to_string(),
        passed,
        output: Some(String::from_utf8_lossy(&output.stderr).to_string()),
        skipped: false,
    });

    Ok(results)
}

fn run_python_tests(verbose: bool) -> Result<Vec<TestResult>> {
    println!("{} {}", "🐍".bold(), "Running Python tests...".cyan());

    let mut results = Vec::new();

    // Check if Python files exist
    let py_files = std::fs::read_dir("py");
    if py_files.is_err() {
        println!("  {} No py/ directory", "⚠️".yellow());
        return Ok(results);
    }

    // Check if pytest exists
    let pytest_check = Command::new("uv")
        .args(["run", "pytest", "--version"])
        .stderr(Stdio::null())
        .output();

    if pytest_check.is_err() || !pytest_check.unwrap().status.success() {
        println!(
            "  {} pytest not available (install with: uv add --dev pytest)",
            "⚠️".yellow()
        );
        return Ok(results);
    }

    // Run pytest
    let output = Command::new("uv")
        .args(["run", "pytest", "py/", "-v", "--tb=short"])
        .output()
        .context("Failed to run pytest")?;

    let stdout = String::from_utf8_lossy(&output.stdout);

    // Check if no tests were collected
    if stdout.contains("collected 0 items") {
        println!("  {} No Python tests found", "⚠️".yellow());
        results.push(TestResult {
            name: "Python tests".to_string(),
            passed: true,
            output: None,
            skipped: true,
        });
        return Ok(results);
    }

    let passed = output.status.success();

    if passed {
        println!("  {} Python tests", "✓".green());
    } else {
        println!("  {} Python tests", "✗".red());
        if verbose {
            println!("{}", stdout.dimmed());
        }
    }

    results.push(TestResult {
        name: "Python tests".to_string(),
        passed,
        output: Some(stdout.to_string()),
        skipped: false,
    });

    Ok(results)
}

fn run_go_tests(verbose: bool) -> Result<Vec<TestResult>> {
    println!("{} {}", "🐹".bold(), "Running Go tests...".cyan());

    let mut results = Vec::new();

    // Check if go exists
    let go_check = Command::new("which").arg("go").output();

    if go_check.is_err() || !go_check.unwrap().status.success() {
        println!("  {} Go not installed", "⚠️".yellow());
        results.push(TestResult {
            name: "Go tests".to_string(),
            passed: true,
            output: None,
            skipped: true,
        });
        return Ok(results);
    }

    // Check if go directory exists
    if !std::path::Path::new("go").exists() {
        println!("  {} No go/ directory", "⚠️".yellow());
        results.push(TestResult {
            name: "Go tests".to_string(),
            passed: true,
            output: None,
            skipped: true,
        });
        return Ok(results);
    }

    // Check if we have Go files
    let has_go_files = std::fs::read_dir("go")
        .map(|entries| {
            entries.filter_map(|e| e.ok()).any(|e| {
                e.path()
                    .extension()
                    .and_then(|ext| ext.to_str())
                    .map(|ext| ext == "go")
                    .unwrap_or(false)
            })
        })
        .unwrap_or(false);

    if !has_go_files {
        println!("  {} No Go files found", "⚠️".yellow());
        results.push(TestResult {
            name: "Go tests".to_string(),
            passed: true,
            output: None,
            skipped: true,
        });
        return Ok(results);
    }

    // Run go test
    let output = Command::new("go")
        .args(["test", "./go/...", "-v"])
        .output()
        .context("Failed to run go test")?;

    let passed = output.status.success();

    if passed {
        println!("  {} Go tests", "✓".green());
    } else {
        println!("  {} Go tests", "✗".red());
        if verbose {
            println!("{}", String::from_utf8_lossy(&output.stdout).dimmed());
        }
    }

    results.push(TestResult {
        name: "Go tests".to_string(),
        passed,
        output: Some(String::from_utf8_lossy(&output.stdout).to_string()),
        skipped: false,
    });

    Ok(results)
}

fn run_e2e_tests(verbose: bool) -> Result<Vec<TestResult>> {
    println!("{} {}", "🔄".bold(), "Running end-to-end tests...".cyan());

    let mut results = Vec::new();

    // Create temp directory for testing
    let temp_dir = TempDir::new()?;

    // Test 1: Version check
    results.push(run_test(
        "Version check",
        || {
            Command::new("uv")
                .args(["run", "dkdc", "--version"])
                .output()
                .map(|o| o.status.success())
                .unwrap_or(false)
        },
        verbose,
    ));

    // Test 2: Help output
    results.push(run_test(
        "Help output",
        || {
            Command::new("uv")
                .args(["run", "dkdc", "--help"])
                .output()
                .map(|o| o.status.success())
                .unwrap_or(false)
        },
        verbose,
    ));

    // Test 3: Dev environment setup
    results.push(run_test(
        "Dev environment setup",
        || match Command::new("uv")
            .args(["run", "dkdc", "dev", "--exit"])
            .output()
        {
            Ok(output) => {
                let stdout = String::from_utf8_lossy(&output.stdout);
                stdout.contains("Setup complete")
            }
            Err(_) => false,
        },
        verbose,
    ));

    // Test 4: Secrets workflow - Fixed version
    results.push(run_test(
        "Secrets workflow",
        || -> bool {
            // Use a unique test secret name to avoid conflicts
            let secret_name = format!("TEST_E2E_SECRET_{}", std::process::id());

            // Set secret
            let set_output = match Command::new("uv")
                .args([
                    "run",
                    "dkdc",
                    "secrets",
                    "set",
                    &secret_name,
                    "--value",
                    "test-value",
                ])
                .output()
            {
                Ok(output) => output,
                Err(_) => return false,
            };

            if !set_output.status.success() {
                if verbose {
                    eprintln!(
                        "Failed to set secret: {}",
                        String::from_utf8_lossy(&set_output.stderr)
                    );
                }
                return false;
            }

            // Get secret
            let get_output = match Command::new("uv")
                .args(["run", "dkdc", "secrets", "get", &secret_name])
                .output()
            {
                Ok(output) => output,
                Err(_) => return false,
            };

            if !get_output.status.success() {
                return false;
            }

            let value = String::from_utf8_lossy(&get_output.stdout);
            if value.trim() != "test-value" {
                // Try without trim in case there's no newline
                if value != "test-value" {
                    eprintln!(
                        "Secret value mismatch: got '{}', expected 'test-value'",
                        value
                    );
                    return false;
                }
            }

            // Delete secret
            match Command::new("uv")
                .args(["run", "dkdc", "secrets", "delete", &secret_name])
                .output()
            {
                Ok(output) => output.status.success(),
                Err(_) => false,
            }
        },
        verbose,
    ));

    // Test 5: Files workflow
    results.push(run_test(
        "Files workflow",
        || -> bool {
            let test_file = temp_dir.path().join("test.txt");
            if std::fs::write(&test_file, "test content").is_err() {
                return false;
            }

            let test_file_str = match test_file.to_str() {
                Some(s) => s,
                None => return false,
            };

            // Add file
            let add_output = match Command::new("uv")
                .args(["run", "dkdc", "files", "add", test_file_str])
                .output()
            {
                Ok(output) => output,
                Err(_) => return false,
            };

            if !add_output.status.success() {
                if verbose {
                    eprintln!(
                        "Failed to add file: {}",
                        String::from_utf8_lossy(&add_output.stderr)
                    );
                }
                return false;
            }

            // List files
            let list_output = match Command::new("uv")
                .args(["run", "dkdc", "files", "list"])
                .output()
            {
                Ok(output) => output,
                Err(_) => return false,
            };

            let stdout = String::from_utf8_lossy(&list_output.stdout);
            stdout.contains("test.txt")
        },
        verbose,
    ));

    // Test 6: Archive workflow
    results.push(run_test(
        "Archive workflow",
        || -> bool {
            let test_dir = temp_dir.path().join("test-project");
            if std::fs::create_dir(&test_dir).is_err() {
                return false;
            }
            if std::fs::write(test_dir.join("file.txt"), "test file").is_err() {
                return false;
            }

            let test_dir_str = match test_dir.to_str() {
                Some(s) => s,
                None => return false,
            };

            match Command::new("uv")
                .args([
                    "run",
                    "dkdc",
                    "archive",
                    test_dir_str,
                    "--name",
                    "test-archive.zip",
                ])
                .output()
            {
                Ok(output) => output.status.success(),
                Err(_) => false,
            }
        },
        verbose,
    ));

    // Test 7: Python-Rust integration
    results.push(run_test(
        "Python-Rust integration",
        || {
            Command::new("uv")
                .args([
                    "run",
                    "python",
                    "-c",
                    "from dkdc import _dkdc; print(_dkdc.__version__)",
                ])
                .output()
                .map(|o| o.status.success())
                .unwrap_or(false)
        },
        verbose,
    ));

    // Test 8: CLI error handling
    results.push(run_test(
        "CLI error handling",
        || match Command::new("uv")
            .args(["run", "dkdc", "nonexistent-command"])
            .output()
        {
            Ok(output) => {
                let stderr = String::from_utf8_lossy(&output.stderr);
                stderr.contains("unrecognized subcommand")
            }
            Err(_) => false,
        },
        verbose,
    ));

    // Print results
    for result in &results {
        if result.skipped {
            println!("  {} {} (skipped)", "⚠️".yellow(), result.name.yellow());
        } else if result.passed {
            println!("  {} {}", "✓".green(), result.name);
        } else {
            println!("  {} {}", "✗".red(), result.name);
            if verbose {
                if let Some(output) = &result.output {
                    for line in output.lines().take(5) {
                        println!("    {}", line.dimmed());
                    }
                }
            }
        }
    }

    Ok(results)
}

fn run_test(name: &str, test_fn: impl FnOnce() -> bool, verbose: bool) -> TestResult {
    let passed = test_fn();

    TestResult {
        name: name.to_string(),
        passed,
        output: if !passed && verbose {
            Some(format!("Test '{}' failed", name))
        } else {
            None
        },
        skipped: false,
    }
}
