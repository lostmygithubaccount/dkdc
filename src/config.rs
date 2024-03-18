use std;

pub fn config_it(vim: bool, env: bool) {
    let program = if vim { "nvim" } else { "code" };
    let filename = if env { ".env" } else { "config.toml" };

    #[allow(deprecated)] // fck Windows
    std::process::Command::new(program)
        .arg(std::env::home_dir().unwrap().join(".dkdc").join(filename))
        .status()
        .expect("whoops");
    return;
}
