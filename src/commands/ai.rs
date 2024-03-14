use reqwest;

use crate::ai;

pub fn ai_testing(user_message: &str) {
    ai::openai::chat_completions(user_message);
}

pub fn ai(url: &str) {
    let body = reqwest::blocking::get(url).unwrap().text().unwrap();

    println!("body = {body:?}");
}
