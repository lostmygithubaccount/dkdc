use dotenv;
use reqwest;
use serde::Serialize;
use serde_json;
use std::env;

#[derive(Serialize)]
struct Message {
    role: String,
    content: String,
}

#[derive(Serialize)]
struct Payload {
    model: String,
    messages: Vec<Message>,
    temperature: f32,
}

pub fn ai_testing(user_message: &str) {
    #[allow(deprecated)] // fck Windows
    let dotenv_path = env::home_dir().unwrap().join(".dkdc").join(".env");
    dotenv::from_path(dotenv_path).unwrap();

    let openai_api_key = match dotenv::var("OPENAI_API_KEY") {
        Ok(key) => key,
        Err(e) => panic!("Set the OPENAI_API_KEY environment variable: {}", e),
    };

    let url = "https://api.openai.com/v1/chat/completions";

    let payload = Payload {
        model: "gpt-4-turbo-preview".to_string(),
        messages: vec![
            Message {
                role: "system".to_string(),
                content: "You are a helpful chatbot.".to_string(),
            },
            Message {
                role: "user".to_string(),
                content: user_message.to_string(),
            },
        ],
        temperature: 1.0,
    };

    let client = reqwest::blocking::Client::new();

    let response = client
        .post(url)
        .header("Authorization", format!("Bearer {}", openai_api_key))
        .json(&payload)
        .send();

    match response {
        Ok(resp) => {
            println!("response_code = {:?}", resp.status());
            println!(
                "{:#?}",
                resp.json::<serde_json::Value>()
                    .unwrap_or_else(|_| serde_json::Value::Null)
            );
        }
        Err(e) => eprintln!("Request failed: {}", e),
    }
}

pub fn ai(url: &str) {
    let body = reqwest::blocking::get(url).unwrap().text().unwrap();

    println!("body = {body:?}");
}
