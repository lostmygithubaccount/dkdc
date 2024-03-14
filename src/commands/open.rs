use itertools::Itertools;
use open;
use std;
use std::collections::HashMap;

pub fn open_it(thing: Option<String>, list: bool) {
    let mut map = HashMap::new();

    #[allow(deprecated)] // fck Windows
    let config_path = std::env::home_dir()
        .unwrap()
        .join(".dkdc")
        .join("config.toml");
    let config = std::fs::read_to_string(config_path).unwrap();
    let config: toml::Value = toml::from_str(config.as_str()).unwrap();
    let open_config = config.get("open").unwrap();
    let open_things = open_config.get("things").unwrap();
    let open_aliases = open_config.get("aliases").unwrap();

    // insert the things
    for (key, value) in open_things.as_table().unwrap() {
        map.insert(key, value.as_str().unwrap().to_string());
    }

    // insert the aliases
    for (key, value) in open_aliases.as_table().unwrap() {
        map.insert(
            key,
            map.get(&value.as_str().unwrap().to_string())
                .unwrap()
                .to_string(),
        );
    }

    // if list is true, print out the things and aliases
    if list {
        let max_length = map.keys().map(|s| s.len()).max().unwrap();
        for (key, value) in map.iter().sorted() {
            println!("{:width$} : {}", key, value, width = max_length);
        }
    }

    // if the thing is in the map, open its value
    match thing {
        Some(thing) => {
            if map.contains_key(&thing) {
                let thing = map.get(&thing).unwrap();
                println!("Opening: {}", thing);
                open::that(thing).unwrap();
                return;
            } else {
                println!("{} not found in open config, opening directly", thing);
                open::that(thing).unwrap();
            }
        }
        _ => {
            println!("Nothing to open");
            return;
        }
    }
}

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
