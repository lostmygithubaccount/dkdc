use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;

/// List files in the virtual filesystem
#[pyfunction]
#[pyo3(signature = (path="./files"))]
fn list_files(path: &str) -> PyResult<Vec<String>> {
    let lake = dkdc_lake::Lake::new()
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    
    lake.list_files(path)
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))
}

/// Add a file to the virtual filesystem
#[pyfunction]
#[pyo3(signature = (file, path=None))]
fn add_file(file: &str, path: Option<&str>) -> PyResult<String> {
    dkdc_files::add_file(file, path)
        .map(|_| format!("Added {}", file))
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))
}

/// Get a secret value
#[pyfunction]
fn get_secret(name: &str) -> PyResult<Option<String>> {
    let lake = dkdc_lake::Lake::new()
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    
    match lake.get_secret(name) {
        Ok(Some(data)) => Ok(Some(String::from_utf8_lossy(&data).to_string())),
        Ok(None) => Ok(None),
        Err(e) => Err(PyRuntimeError::new_err(e.to_string())),
    }
}

/// Set a secret value
#[pyfunction]
fn set_secret(name: &str, value: &str) -> PyResult<()> {
    let lake = dkdc_lake::Lake::new()
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    
    lake.set_secret(name, value.as_bytes())
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))
}

/// List all secrets
#[pyfunction]
fn list_secrets() -> PyResult<Vec<String>> {
    let lake = dkdc_lake::Lake::new()
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    
    lake.list_secrets()
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))
}

/// Delete a secret
#[pyfunction]
fn delete_secret(name: &str) -> PyResult<bool> {
    let lake = dkdc_lake::Lake::new()
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    
    lake.delete_secret(name)
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))
}

/// Launch development REPL
#[pyfunction]
#[pyo3(signature = (sql=false, exit=false))]
fn launch_dev(sql: bool, exit: bool) -> PyResult<()> {
    let dev = dkdc_dev::Dev::new()
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    
    if exit {
        if !sql {
            dev.ensure_python_env()
                .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        }
        println!("Setup complete");
        return Ok(());
    }
    
    let mode = if sql { 
        dkdc_dev::DevMode::Sql 
    } else { 
        dkdc_dev::DevMode::Python 
    };
    
    dev.launch(mode)
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))
}

/// Get DuckDB connection string for data lake
#[pyfunction]
fn get_connection_string() -> PyResult<String> {
    let lake = dkdc_lake::Lake::new()
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    
    Ok(lake.get_sql_commands())
}

/// Run the CLI with given arguments
#[pyfunction]
fn run_cli(args: Vec<String>) -> PyResult<i32> {
    // Always prepend "dkdc" as the program name
    let mut cli_args = vec!["dkdc".to_string()];
    cli_args.extend(args);
    
    match dkdc_cli::run_cli(cli_args) {
        Ok(_) => Ok(0),
        Err(e) => {
            eprintln!("{}", e);
            Ok(1)
        }
    }
}


/// Python module definition
#[pymodule]
fn _dkdc(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(list_files, m)?)?;
    m.add_function(wrap_pyfunction!(add_file, m)?)?;
    m.add_function(wrap_pyfunction!(get_secret, m)?)?;
    m.add_function(wrap_pyfunction!(set_secret, m)?)?;
    m.add_function(wrap_pyfunction!(list_secrets, m)?)?;
    m.add_function(wrap_pyfunction!(delete_secret, m)?)?;
    m.add_function(wrap_pyfunction!(launch_dev, m)?)?;
    m.add_function(wrap_pyfunction!(get_connection_string, m)?)?;
    m.add_function(wrap_pyfunction!(run_cli, m)?)?;
    m.add("__version__", dkdc_common::version::PKG_VERSION)?;
    Ok(())
}