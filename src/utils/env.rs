use dotenv;
use std::env;

pub fn load_dotenv() {
    #[allow(deprecated)] // fck Windows
    let dotenv_path = env::home_dir().unwrap().join(".dkdc").join(".env");
    dotenv::from_path(dotenv_path).unwrap();
}

pub fn get_openai_api_key() -> String {
    match dotenv::var("OPENAI_API_KEY") {
        Ok(key) => key,
        Err(e) => panic!("Set the OPENAI_API_KEY environment variable: {}", e),
    }
}
